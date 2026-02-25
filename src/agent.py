import logging
import os

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    MultimodalAgent,
    JobContext,
    AgentServer,
    cli,
)
from livekit.plugins import openai

from ist_knowledge import load_ist_corpus, build_vector_index, build_ist_context

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Load IST knowledge base
IST_DOCS = load_ist_corpus()
if not os.getenv("SKIP_VECTOR_INDEX"):
    build_vector_index(IST_DOCS)

server = AgentServer()


# Only forward to admissions when query cannot be answered from KB
HUMAN_ESCALATION_MESSAGE = (
    "We will forward this query to our admissions team. Please tell me your phone number so we can call you back."
)

# Minimal embedded context when data folder is missing on deploy
EMBEDDED_FALLBACK_CONTEXT = """
TITLE: IST Departments and Programs
CONTENT: IST has 9 departments. BS programs: Aerospace, Avionics, Electrical, Computer, Mechanical, Materials Science, Biotechnology, Computer Science, Software Engineering, Data Science, AI, Space Science, Physics, Mathematics. MS and PhD in Aerospace, Electrical, Materials, Mechanical, CS, Mathematics, Physics, Astronomy. Admissions: 051 9075100, ist.edu.pk/admission.

TITLE: IST Fee Structure
CONTENT: BS Aerospace/Electrical/Avionics/Mechanical: about 1 lakh 48 thousand per semester. Materials: 1 lakh 42 thousand. Computing (CS, Software Eng, Data Science, AI): 1 lakh 26 thousand per semester. Other BS (Space Science, Mathematics, Physics, Biotechnology): 1 lakh 2 thousand per semester. One-time charges 49 thousand. MS about 1 lakh 20 thousand per year. PhD about 1 lakh 30 thousand per year. Admissions 051 9075100.
""".strip()


def build_ist_system_instructions():
    """Build comprehensive system instructions grounded in IST knowledge base."""
    return (
        "Respond only in English.\n\n"
        "You are an IST (Institute of Space Technology) admissions agent on a phone call.\n\n"
        "CRITICAL ESCALATION RULE:\n"
        "✓ DO ANSWER from knowledge base IF: programs, fees, deadlines, merit, departments, eligibility, contact info, or FAQs\n"
        "✗ ONLY escalate IF: caller wants to apply now, needs personalized advice, asks about specific documents, or something is clearly NOT in the KB\n"
        "✗ NEVER escalate just because the answer is complex—you HAVE this information in the context below\n\n"
        "BEHAVIOR RULES (CRITICAL — follow strictly):\n"
        "- NEVER repeat or paraphrase what the caller said. Do NOT say 'You asked about...', 'You want to know about...', "
        "'Since you are asking about...', 'Regarding your question...', or 'As for your question...'. Start your reply with the direct answer only.\n"
        "- NEVER say 'What do you want?', 'What would you like?', 'What do you need?', or 'What can I help you with?' — always give a direct answer.\n"
        "- NEVER speak on your own or add extra sentences. Only respond to what was asked.\n"
        "- Keep answers SHORT: 1-2 sentences max. No filler, no pleasantries, no 'Sure!', no 'Great question!', no 'Absolutely!'.\n"
        "- Do NOT add 'Is there anything else I can help with?' or similar unless the caller explicitly asks to end the call.\n"
        "- Be direct and factual. Answer the question, nothing more.\n\n"
        "FEES: When the caller asks about fee, fees, fee structure, or fee of programs:\n"
        "- Always state amounts in Pakistani Rupees (PKR) only. Use 'lakh and thousand' (e.g. '1 lakh 26 thousand rupees').\n"
        "- For BS Physics, BS Space Science, BS Mathematics, BS Biotechnology: the fee is 1 lakh 2 thousand rupees per semester.\n"
        "- For Computing programs (CS, Software Engineering, Data Science, AI): 1 lakh 26 thousand per semester.\n"
        "- For Engineering programs (Aerospace, Electrical, Avionics, Mechanical): 1 lakh 48 thousand per semester.\n\n"
        "PROGRAMS: When listing programs offered by IST, include ALL Computing programs: "
        "BS Computer Science, BS Software Engineering, BS Data Science, BS Artificial Intelligence (BS AI).\n\n"
        "MERIT AND AGGREGATE: When caller asks 'will I get admission' or about merit:\n"
        "- For Engineering programs: use Matric + FSC + Entry Test in formula (10%+40%+50%)\n"
        "- For Non-Engineering: use Matric + FSC only (50%+50%)\n"
        "- Only compute aggregate if caller provides marks; ask for marks if they don't.\n"
        "- Never predict admission; be hopeful and suggest checking portal.\n\n"
        "CRITICAL RULES:\n"
        "1) Answer ONLY from the context provided below. Do NOT guess or make up figures.\n"
        "2) Do NOT refuse to answer or escalate when context contains relevant information.\n"
        "3) 1-2 sentences max. No filler. No repeating the question.\n"
        "4) Do not say goodbye unless the caller asks to end the call.\n"
        "5) Only use escalation message when query is TRULY outside KB (rare)."
    )


@server.rtc_session()
async def my_agent(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Build IST-aware system instructions
    base_instructions = build_ist_system_instructions()
    
    # Build context from knowledge base (or use fallback if KB not available)
    ist_context = build_ist_context("IST admission programs fees merit contact", docs=IST_DOCS, max_chars=3000)
    if ist_context.startswith("No highly relevant IST website content was found"):
        if IST_DOCS:
            snippets = []
            for d in IST_DOCS[:5]:
                snippet = d.text[:600]
                snippets.append(f"TITLE: {d.title or 'N/A'}\nCONTENT: {snippet}")
            ist_context = "\n\n".join(snippets)[:4000]
        if ist_context.startswith("No highly relevant IST website content was found"):
            logger.warning("Using embedded fallback context (data folder not loaded).")
            ist_context = EMBEDDED_FALLBACK_CONTEXT
    
    # Combine system instructions with IST context
    full_instructions = (
        f"{base_instructions}\n\n"
        f"IST KNOWLEDGE BASE CONTEXT:\n{ist_context}\n\n"
        f"ESCALATION MESSAGE (only use if you cannot answer from above context): \"{HUMAN_ESCALATION_MESSAGE}\""
    )
    
    logger.info("IST Agent initialized with %d KB documents", len(IST_DOCS))
    
    # Initialize OpenAI Realtime model with IST instructions
    model = openai.realtime.RealtimeModel(
        instructions=full_instructions,
        voice="shimmer",
        temperature=0.7,
        modalities=["audio", "text"],
    )

    agent = MultimodalAgent(model=model, fnc_ctx=None)
    agent.start(ctx.room)



if __name__ == "__main__":
    print("Starting agent...")
    cli.run_app(server)
