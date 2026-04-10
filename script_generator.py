"""
AI Movie Script Generator using RAG + LangChain + Groq + FAISS
---------------------------------------------------------------
Usage:
  Step 1 — Ingest your scripts:
      python script_generator.py --ingest

  Step 2 — Generate a new screenplay:
      python script_generator.py --generate
"""

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPTS_DIR   = Path("scripts_data")
FAISS_DIR     = Path("faiss_db")
OUTPUT_DIR    = Path("output")
GROQ_MODEL    = "llama-3.3-70b-versatile"   # Latest Groq model (2025)
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 150
TOP_K         = 6


# ── Embeddings (free, runs locally) ──────────────────────────────────────────
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


# ── 1. Ingestion ──────────────────────────────────────────────────────────────
def ingest_scripts():
    print("\n📂  Loading scripts from:", SCRIPTS_DIR)

    loaders = []
    for fpath in SCRIPTS_DIR.iterdir():
        if fpath.suffix == ".pdf":
            loaders.append(PyPDFLoader(str(fpath)))
        elif fpath.suffix == ".txt":
            loaders.append(TextLoader(str(fpath), encoding="utf-8"))

    if not loaders:
        print("⚠️  No .txt or .pdf files found in scripts_data/")
        print("    Add some movie scripts and re-run with --ingest")
        return

    all_docs = []
    for loader in loaders:
        docs = loader.load()
        all_docs.extend(docs)
        print(f"   ✓ Loaded: {loader.file_path}  ({len(docs)} chunks)")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "INT.", "EXT.", " ", ""],
    )
    chunks = splitter.split_documents(all_docs)
    print(f"\n✂️   Split into {len(chunks)} chunks")

    print("🔢  Embedding chunks with HuggingFace (local, free)…")
    embeddings = get_embeddings()

    vectorstore = FAISS.from_documents(chunks, embeddings)
    FAISS_DIR.mkdir(exist_ok=True)
    vectorstore.save_local(str(FAISS_DIR))

    print(f"✅  Vector store saved to {FAISS_DIR}/")
    print(f"    Total chunks indexed: {len(chunks)}")


# ── 2. Script Generation ──────────────────────────────────────────────────────
SCREENPLAY_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a professional Hollywood screenwriter with 20+ years of experience.
You study screenplay excerpts closely and write in proper industry-standard format.

Use the following screenplay excerpts as style and structural reference:
──────────────────────────────────────────────
{context}
──────────────────────────────────────────────

Now write a FULL, original screenplay based on this brief:
{question}

Your screenplay MUST include:
- TITLE PAGE (title, written by, logline)
- FADE IN:
- At least 5 fully developed scenes using INT./EXT. sluglines
- Rich action lines with vivid description
- Natural, character-specific dialogue
- Scene transitions (CUT TO:, DISSOLVE TO:, etc.)
- FADE OUT. / THE END

Write the complete screenplay now. Do not summarise — write every scene in full detail.
""",
)


def build_retriever():
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        str(FAISS_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore.as_retriever(search_kwargs={"k": TOP_K})


def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def generate_script(brief: str) -> str:
    if not FAISS_DIR.exists():
        raise FileNotFoundError(
            "Vector store not found. Run  python script_generator.py --ingest  first."
        )

    print("\n🔍  Retrieving relevant script excerpts…")
    retriever = build_retriever()

    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0.9,
        max_tokens=4096,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | SCREENPLAY_PROMPT
        | llm
        | StrOutputParser()
    )

    print(f"✍️   Generating screenplay with Groq ({GROQ_MODEL})…\n")
    print("=" * 70)

    full_script = ""
    for chunk in chain.stream(brief):
        print(chunk, end="", flush=True)
        full_script += chunk

    print("\n" + "=" * 70)
    return full_script


def save_script(script: str, title: str = "screenplay"):
    OUTPUT_DIR.mkdir(exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in " _-" else "" for c in title).strip().replace(" ", "_")
    outfile = OUTPUT_DIR / f"{safe_title}.txt"
    outfile.write_text(script, encoding="utf-8")
    print(f"\n💾  Screenplay saved to: {outfile}")
    return outfile


# ── CLI ───────────────────────────────────────────────────────────────────────
def prompt_user_for_brief() -> tuple[str, str]:
    print("\n" + "═" * 60)
    print("  🎬  AI MOVIE SCRIPT GENERATOR  (Powered by Groq)")
    print("═" * 60)

    title   = input("\nMovie title: ").strip() or "Untitled"
    genre   = input("Genre (e.g. thriller, sci-fi, romance): ").strip()
    logline = input("One-sentence logline / plot idea: ").strip()
    chars   = input("Main characters (name + short description, comma-separated): ").strip()
    tone    = input("Tone (e.g. dark and tense, witty and fast-paced): ").strip()
    setting = input("Setting / world (e.g. 1980s New York, dystopian future): ").strip()

    brief = f"""Title: {title}
Genre: {genre}
Logline: {logline}
Main characters: {chars}
Tone: {tone}
Setting: {setting}"""

    return brief, title


def main():
    parser = argparse.ArgumentParser(description="AI Movie Script Generator (RAG + LangChain + Groq)")
    parser.add_argument("--ingest",   action="store_true", help="Ingest scripts from scripts_data/")
    parser.add_argument("--generate", action="store_true", help="Generate a new screenplay interactively")
    parser.add_argument("--brief",    type=str,            help="Screenplay brief (skips interactive prompts)")
    parser.add_argument("--title",    type=str, default="screenplay", help="Output file title")
    args = parser.parse_args()

    if not args.ingest and not args.generate and not args.brief:
        parser.print_help()
        return

    if args.ingest:
        ingest_scripts()

    if args.generate or args.brief:
        if args.brief:
            brief = args.brief
            title = args.title
        else:
            brief, title = prompt_user_for_brief()

        script = generate_script(brief)
        save_script(script, title)


if __name__ == "__main__":
    main()
