import os
from pathlib import Path
import uuid

from dotenv import load_dotenv


load_dotenv()

SESSIONS_DIR = "./sessions"

os.makedirs(SESSIONS_DIR, exist_ok=True)


def get_session_dirs(session_id):
    session_uuid = str(uuid.UUID(session_id))

    session_dir = Path(SESSIONS_DIR) / session_uuid

    upload_dir = session_dir / "uploaded_pdfs"
    chroma_dir = session_dir / "chroma_store"

    upload_dir.mkdir(parents=True, exist_ok=True)
    chroma_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir, chroma_dir


def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"batch_size": 8}
    )

def load_vectorstore(uploaded_files, session_id):

    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma

    upload_dir, chroma_dir = get_session_dirs(session_id)

    embed_model = get_embeddings()

    vectorstore = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embed_model
    )

    for file in uploaded_files:

        save_path = upload_dir / file.filename

        with open(save_path, "wb") as f:
            f.write(file.file.read())

        loader = PyPDFLoader(str(save_path))

        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(documents)

        vectorstore.add_documents(chunks)

        print(f"✅ Added {len(chunks)} chunks from {file.filename}")

    print("✅ Documents added to ChromaDB")


def delete_document(filename, session_id):

    from langchain_chroma import Chroma

    upload_dir, chroma_dir = get_session_dirs(session_id)

    embed_model = get_embeddings()

    vectorstore = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embed_model
    )

    source_path = str(upload_dir / filename)

    results = vectorstore.get(
        where={"source": source_path}
    )

    ids = results.get("ids", [])

    if ids:
        vectorstore.delete(ids=ids)

    file_path = Path(source_path)

    if file_path.exists():
        file_path.unlink()

    return len(ids)


def list_documents(session_id):

    upload_dir, _ = get_session_dirs(session_id)

    return [
        file.name
        for file in upload_dir.iterdir()
        if file.is_file() and file.suffix.lower() == ".pdf"
    ]