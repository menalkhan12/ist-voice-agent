import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# Resolve data dir: same repo as this file (parent of src), or cwd, or cwd's parent (for Render: cd src && gunicorn)
def _data_dir() -> Path:
    for root in [
        Path(__file__).resolve().parents[1],
        Path.cwd(),
        Path.cwd().parent,
    ]:
        d = root / "data"
        if (d / "FEE_STRUCTURE.txt").exists() or (d / "IST_FULL_WEBSITE_MANUAL.txt").exists():
            return d
    return Path(__file__).resolve().parents[1] / "data"

_DATA_DIR = _data_dir()
DATA_PATH = _DATA_DIR / "99_MASTER_JSON.json"
MERIT_CRITERIA_PATH = _DATA_DIR / "MERIT_CRITERIA_AND_AGGREGATE.txt"
CLOSING_MERIT_PATH = _DATA_DIR / "CLOSING_MERIT_HISTORY.txt"
FEE_STRUCTURE_PATH = _DATA_DIR / "FEE_STRUCTURE.txt"
ADMISSION_INFO_PATH = _DATA_DIR / "ADMISSION_INFO.txt"
ADMISSION_DATES_PATH = _DATA_DIR / "ADMISSION_DATES_AND_STATUS.txt"
IST_SUMMARY_PATH = _DATA_DIR / "IST_DEPARTMENTS_AND_PROGRAMS_SUMMARY.txt"
WEBSITE_FULL_PATH = _DATA_DIR / "WEBSITE_FULL.txt"
MANUAL_FULL_PATH = _DATA_DIR / "IST_FULL_WEBSITE_MANUAL.txt"
TRANSPORT_FAQS_PATH = _DATA_DIR / "TRANSPORT_HOSTEL_FAQS.txt"
ADMISSION_FAQS_COMPLETE_PATH = _DATA_DIR / "ADMISSION_FAQS_COMPLETE.txt"
DATA_DIR = _DATA_DIR
CHROMA_PERSIST_DIR = _DATA_DIR / "chroma_db"

# Vector search: populated by build_vector_index(); used by search() when available
_vector_collection = None
_docs_list: List["ISTDocument"] = []
_VECTOR_AVAILABLE = False

try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    _VECTOR_AVAILABLE = True
except Exception as e:
    logger.info("Vector search unavailable (chromadb/sentence-transformers): %s. Using keyword search.", e)


@dataclass
class ISTDocument:
    url: str
    title: str
    text: str


def load_ist_corpus() -> List[ISTDocument]:
    """Load IST website content: scraped JSON (if present) plus all data/*.txt files (merit, fees, manual, FAQs, etc.)."""
    docs: List[ISTDocument] = []

    if DATA_PATH.exists():
        with DATA_PATH.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        pages = raw.get("pages", {})
        for url, page in pages.items():
            title = page.get("title") or ""
            blocks = page.get("text_blocks") or []
            if isinstance(blocks, list) and blocks:
                text = " ".join(blocks)
            else:
                text = page.get("text") or ""
            text = " ".join(text.split())
            if text:
                docs.append(ISTDocument(url=url, title=title, text=text))
        logger.info("Loaded %d pages from %s", len(docs), DATA_PATH.name)
    else:
        logger.warning("IST knowledge base JSON not found at %s; loading from data/*.txt only.", DATA_PATH)

    # Add merit/aggregate criteria so RAG can answer merit and admission-chance questions
    if MERIT_CRITERIA_PATH.exists():
        try:
            merit_text = " ".join(MERIT_CRITERIA_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/MERIT_CRITERIA_AND_AGGREGATE.txt",
                    title="IST Merit Criteria and Aggregate Calculation",
                    text=merit_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load merit criteria file: %s", e)

    # Add fee structure (BS Electrical, MS, PhD) so RAG can answer fee questions
    if FEE_STRUCTURE_PATH.exists():
        try:
            fee_text = " ".join(FEE_STRUCTURE_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/FEE_STRUCTURE.txt",
                    title="IST Fee Structure BS MS PhD",
                    text=fee_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load fee structure file: %s", e)

    # Add admission contact and links (phone, website, fee pages)
    if ADMISSION_INFO_PATH.exists():
        try:
            adm_text = " ".join(ADMISSION_INFO_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/ADMISSION_INFO.txt",
                    title="IST Admissions Contact and Links",
                    text=adm_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load admission info file: %s", e)

    # Add admission dates and status (when do admissions start, are they open, deadlines)
    if ADMISSION_DATES_PATH.exists():
        try:
            dates_text = " ".join(ADMISSION_DATES_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/ADMISSION_DATES_AND_STATUS.txt",
                    title="IST Admission Dates and Status",
                    text=dates_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load admission dates file: %s", e)

    # Add closing merit history (last 6 years per program) for trend and "will merit increase/decrease" questions
    if CLOSING_MERIT_PATH.exists():
        try:
            closing_text = " ".join(CLOSING_MERIT_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/CLOSING_MERIT_HISTORY.txt",
                    title="IST Closing Merit History and Trend",
                    text=closing_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load closing merit file: %s", e)

    # Add transport, hostel, financial aid, application FAQs (multiple programs, change major, edit application, test-optional, high school, interview, laundry)
    if TRANSPORT_FAQS_PATH.exists():
        try:
            faq_text = " ".join(TRANSPORT_FAQS_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/TRANSPORT_HOSTEL_FAQS.txt",
                    title="IST Transport Hostel and Admission FAQs",
                    text=faq_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load transport/FAQs file: %s", e)

    # Add full admission FAQs (100 Q&As: deadlines, eligibility, entry tests, programs, fees, scholarships, documents, hostels, merit list, career)
    if ADMISSION_FAQS_COMPLETE_PATH.exists():
        try:
            faq_full_text = " ".join(ADMISSION_FAQS_COMPLETE_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/ADMISSION_FAQS_COMPLETE.txt",
                    title="IST Admission FAQs Complete",
                    text=faq_full_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load admission FAQs complete file: %s", e)

    # Add IST departments and programs summary (9 departments, all BS/MS/PhD programs)
    if IST_SUMMARY_PATH.exists():
        try:
            summary_text = " ".join(IST_SUMMARY_PATH.read_text(encoding="utf-8").split())
            docs.append(
                ISTDocument(
                    url="data/IST_DEPARTMENTS_AND_PROGRAMS_SUMMARY.txt",
                    title="IST Departments and Programs Summary",
                    text=summary_text,
                )
            )
        except Exception as e:
            logger.warning("Could not load IST summary file: %s", e)

    # Add full website scrape (all pages and subpages from ist.edu.pk) when available
    if WEBSITE_FULL_PATH.exists():
        try:
            full_text = WEBSITE_FULL_PATH.read_text(encoding="utf-8")
            if full_text.strip():
                docs.append(
                    ISTDocument(
                        url="data/WEBSITE_FULL.txt",
                        title="IST Website Full (All Pages and Subpages)",
                        text=" ".join(full_text.split()),
                    )
                )
                logger.info("Loaded WEBSITE_FULL.txt into knowledge base.")
        except Exception as e:
            logger.warning("Could not load WEBSITE_FULL file: %s", e)

    # Add manually compiled full website reference (all 9 sections, subpages, contacts, facilities, etc.)
    # Split by === Section === headers so RAG retrieves only relevant sections (e.g. ICUBE-Q, Al Khwarizmi, NCGSA).
    if MANUAL_FULL_PATH.exists():
        try:
            raw = MANUAL_FULL_PATH.read_text(encoding="utf-8")
            if raw.strip():
                import re
                section_pattern = re.compile(r"^===\s*(.+?)\s*===\s*$", re.MULTILINE)
                parts = section_pattern.split(raw)
                # parts[0] = text before first ===, parts[1]=title1, parts[2]=content1, parts[3]=title2, ...
                if len(parts) >= 3:
                    for i in range(1, len(parts) - 1, 2):
                        title = parts[i].strip()
                        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
                        content = " ".join(content.split())
                        if content and len(content) > 50:
                            docs.append(
                                ISTDocument(
                                    url=f"data/IST_FULL_WEBSITE_MANUAL.txt#{title[:50]}",
                                    title=f"IST Manual: {title}",
                                    text=content,
                                )
                            )
                    logger.info("Loaded IST_FULL_WEBSITE_MANUAL.txt in %d sections.", (len(parts) - 1) // 2)
                else:
                    # fallback: single doc
                    manual_text = " ".join(raw.split())
                    docs.append(
                        ISTDocument(
                            url="data/IST_FULL_WEBSITE_MANUAL.txt",
                            title="IST Full Website Manual Reference (All Sections)",
                            text=manual_text,
                        )
                    )
                    logger.info("Loaded IST_FULL_WEBSITE_MANUAL.txt as single document.")
        except Exception as e:
            logger.warning("Could not load manual website file: %s", e)

    for name, title in [
        ("03_ABOUT.txt", "IST About"),
        ("05_DEPARTMENTS.txt", "IST Departments"),
        ("06_FACILITIES.txt", "IST Facilities"),
        ("07_FACULTY.txt", "IST Faculty"),
        ("11_RESEARCH.txt", "IST Research"),
    ]:
        path = DATA_DIR / name
        if path.exists():
            try:
                text = " ".join(path.read_text(encoding="utf-8").split())
                if text:
                    docs.append(ISTDocument(url=f"data/{name}", title=title, text=text))
            except Exception as e:
                logger.warning("Could not load %s: %s", name, e)

    logger.info("Loaded %d IST documents total (data folder).", len(docs))
    logger.info("DATA_DIR resolved to: %s (FEE_STRUCTURE exists: %s)", DATA_DIR, FEE_STRUCTURE_PATH.exists())
    return docs


def get_data_dir_status() -> dict:
    """For debug endpoint: report whether data folder was found and doc count."""
    return {
        "data_dir": str(DATA_DIR),
        "fee_structure_exists": FEE_STRUCTURE_PATH.exists(),
        "manual_exists": MANUAL_FULL_PATH.exists(),
    }


def simple_search(query: str, docs: List[ISTDocument], top_k: int = 5) -> List[ISTDocument]:
    """Very lightweight keyword-based retrieval over IST pages.

    This avoids needing embeddings or a separate vector DB while still
    grounding the LLM in real IST content.
    """
    query = (query or "").strip().lower()
    if not docs:
        return []

    # Allow 2+ char terms so "bs", "is", "ms" match; fallback so we never return empty when we have docs
    terms = [t for t in query.replace("?", " ").replace(",", " ").split() if len(t) >= 2]
    if not terms:
        terms = ["ist", "admission", "programs"]

    scored: list[tuple[float, ISTDocument]] = []
    for doc in docs:
        text_l = doc.text.lower()
        score = 0.0
        for t in terms:
            if t in text_l:
                score += 1.0
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]]


def build_vector_index(docs: List[ISTDocument]) -> None:
    """Build a ChromaDB vector index from the document list for semantic search.
    Call once after load_ist_corpus(). Enables synonym/paraphrase matching (e.g. 'cost' vs 'fees').
    """
    global _vector_collection, _docs_list
    if not _VECTOR_AVAILABLE or not docs:
        return
    try:
        CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
        coll = client.get_or_create_collection(
            name="ist_knowledge",
            embedding_function=ef,
            metadata={"description": "IST scraped pages + merit criteria"},
        )
        ids = [str(i) for i in range(len(docs))]
        documents = [f"{d.title} {d.text}" for d in docs]
        coll.upsert(ids=ids, documents=documents)
        _vector_collection = coll
        _docs_list = docs
        logger.info("Built vector index for %d documents (ChromaDB + sentence-transformers).", len(docs))
    except Exception as e:
        logger.warning("Could not build vector index: %s. Using keyword search only.", e)
        _vector_collection = None
        _docs_list = docs


def vector_search(query: str, top_k: int = 5) -> List[ISTDocument]:
    """Semantic search using embeddings. Returns top_k documents by similarity.
    Resolves synonyms (e.g. 'cost' vs 'fees'). Requires build_vector_index() to have been called.
    """
    global _vector_collection, _docs_list
    if not _VECTOR_AVAILABLE or _vector_collection is None or not _docs_list:
        return []
    try:
        results = _vector_collection.query(query_texts=[query], n_results=min(top_k, len(_docs_list)))
        ids = results["ids"][0] if results["ids"] else []
        out = []
        for id_ in ids:
            idx = int(id_)
            if 0 <= idx < len(_docs_list):
                out.append(_docs_list[idx])
        return out
    except Exception as e:
        logger.warning("Vector search failed: %s", e)
        return []


def search(query: str, docs: List[ISTDocument], top_k: int = 5) -> List[ISTDocument]:
    """Retrieve top_k documents for the query. Uses vector (semantic) search if available, else keyword search."""
    if not query or not docs:
        return []
    if _vector_collection is not None and _docs_list and len(_docs_list) == len(docs):
        hits = vector_search(query, top_k=top_k)
        if hits:
            return hits
    return simple_search(query, docs, top_k=top_k)

