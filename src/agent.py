import logging
from livekit.agents import JobContext, JobProcess, WorkerOptions, cli, llm
from livekit.agents.voice_pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero, cartesia
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Setup logging for Render logs
logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

# 1. Initialize RAG (ChromaDB)
# Ensure your 'chroma_db' folder is uploaded to your GitHub
embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def get_context(query: str):
    """Retrieve info from ChromaDB"""
    docs = db.similarity_search(query, k=3)
    if not docs:
        return None
    return "\n".join([d.page_content for d in docs])

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a confident Admission Assistant. Use the provided knowledge base to answer. "
            "1. If the info is in the knowledge base, answer accurately. Do not change your answer even if challenged. "
            "2. If it is NOT in the knowledge base, check if it can be answered with a simple 'Yes' or 'No'. "
            "3. If you absolutely cannot answer, say: 'I don't have that specific detail right now. I will forward this to the admission office. Please tell me your phone number so they can call you.' "
            "4. When a user gives a phone number, repeat it back to confirm and say 'Thank you, we will contact you.'"
            "Stay professional and never repeat the user's question back to them."
        ),
    )

    await ctx.connect()

    # 2. Configure Agent with Interruption Handling (VAD)
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(), # Ignores background noise, reacts to speech
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(), # Low latency TTS
        chat_ctx=initial_ctx,
        allow_interruptions=True,
        interrupt_speech_duration=0.5, # Stops speaking after 0.5s of user speech
        min_endpointing_delay=0.5,
    )

    @agent.on("user_speech_committed")
    def on_user_speech(msg: llm.ChatMessage):
        """This handles the RAG and Logic before the LLM speaks"""
        query = msg.content
        context = get_context(query)
        
        if context:
            # Inject context into the conversation hiddenly
            agent.chat_ctx.append(role="system", text=f"Context for this query: {context}")
        
        # If the user provides a phone number, log it
        if any(char.isdigit() for char in query) and len(query) > 7:
            with open("leads.log", "a") as f:
                f.write(f"Lead: {query}\n")
            logger.info(f"Saved lead: {query}")

    agent.start(ctx.room)
    await agent.say("Hello! This is the admission office. How can I help you today?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))