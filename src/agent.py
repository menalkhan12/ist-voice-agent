import os
import logging
from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_pipeline import VoicePipelineAgent
from livekit.plugins import groq, openai, silero, google

# Standard SQLite fix for Render
try:
    import pysqlite3 as sqlite3
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text="You are an IST Admission Assistant. Be confident. Use the provided context."
    )

    await ctx.connect()

    # Use Groq for STT and LLM to keep it free and fast
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=groq.STT(model="whisper-large-v3"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=google.TTS(), # Use Google AI Studio free tier
        chat_ctx=initial_ctx,
        allow_interruptions=True,
    )

    agent.start(ctx.room)
    await agent.say("Hello! This is IST Admissions. How can I help?")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))