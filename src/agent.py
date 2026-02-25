# FIX FOR RENDER SQLITE VERSION
try:
    import pysqlite3 as sqlite3
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import os
import logging
from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_pipeline import VoicePipelineAgent
from livekit.plugins import groq, xai, google, silero
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("admission-agent")

# Initialize Knowledge Base
embeddings = OpenAIEmbeddings() 
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def get_context(query: str):
    docs = db.similarity_search(query, k=3)
    return "\n".join([d.page_content for d in docs]) if docs else None

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are the IST Admission Assistant powered by Grok. "
            "Use the provided context to answer. If you don't know, ask for a phone number. "
            "Be confident and do not let the user confuse you."
        ),
    )

    await ctx.connect()

    # THE PERFECT PIPELINE
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=groq.STT(model="whisper-large-v3"), # Fast & Free
        llm=xai.LLM(model="grok-beta"),          # High Intelligence
        tts=google.TTS(),                       # Gemini TTS (Free Tier)
        chat_ctx=initial_ctx,
        allow_interruptions=True,
        interrupt_speech_duration=0.5,
    )

    @agent.on("user_speech_committed")
    def on_user_speech(msg: llm.ChatMessage):
        context = get_context(msg.content)
        if context:
            agent.chat_ctx.append(role="system", text=f"Context: {context}")
        
        # Lead Capture
        if any(char.isdigit() for char in msg.content) and len(msg.content) >= 10:
            with open("leads.log", "a") as f:
                f.write(f"Lead: {msg.content}\n")

    agent.start(ctx.room)
    await agent.say("Hello, IST Admissions here. How can I help you?")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))