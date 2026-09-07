import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from langchain_core.embeddings import Embeddings

load_dotenv()

SESSIONS_DIR = "./sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)


# ---------------- Session Directories ---------------- #

def get_session_dirs(session_id):
    session_uuid = str(uuid.UUID(session_id))

    session_dir = Path(SESSIONS_DIR) / session_uuid
    upload_dir = session_dir / "uploaded_pdfs"
    chroma_dir = session_dir / "chroma_store"

    upload_dir.mkdir(parents=True, exist_ok=True)
    chroma_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir, chroma_dir


# ---------------- Gemini Embeddings ---------------- #

class GeminiEmbeddings(Embeddings):

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def embed_documents(self, texts):
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config={
                "task_type": "RETRIEVAL_DOCUMENT"
            }
        )

        return [
            embedding.values
            for embedding in response.embeddings
        ]

    def embed_query(self, text):
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config={
                "task_type": "RETRIEVAL_QUERY"
            }
        )

        return response.embeddings[0].values


def get_embeddings():
    return GeminiEmbeddings()


# ---------------- Upload PDFs & Create Vector Store ---------------- #

def load_vectorstore(uploaded_files, session_id):

    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma

    upload_dir, chroma_dir = get_session_dirs(session_id)

    vectorstore = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=get_embeddings()
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    for file in uploaded_files:

        save_path = upload_dir / file.filename

        # Prevent duplicate filenames
        if save_path.exists():
            raise ValueError(
                f"{file.filename} already exists."
            )

        # Save PDF
        with open(save_path, "wb") as f:
            f.write(file.file.read())

        # Load PDF
        loader = PyPDFLoader(str(save_path))
        documents = loader.load()

        # Split PDF into chunks
        chunks = splitter.split_documents(documents)

        # Add chunks to ChromaDB
        vectorstore.add_documents(chunks)

        print(
            f"Added {len(chunks)} chunks from {file.filename}"
        )

    print("Documents added to ChromaDB")


# ---------------- Delete PDF ---------------- #

def delete_document(filename, session_id):

    from langchain_chroma import Chroma

    upload_dir, chroma_dir = get_session_dirs(session_id)

    vectorstore = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=get_embeddings()
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


# ---------------- List Uploaded PDFs ---------------- #

def list_documents(session_id):

    upload_dir, _ = get_session_dirs(session_id)

    return [
        file.name
        for file in upload_dir.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".pdf"
    ]