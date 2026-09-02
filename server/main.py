from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from modules.llm import get_llm_chain
from modules.query_handlers import query_chain
from logger import logger
from modules.load_vectorstore import (
    load_vectorstore,
    get_embeddings,
    delete_document,
    list_documents
)
from langchain_chroma import Chroma

app = FastAPI(title="RagBot2.0")


# allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def catch_exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)

    except Exception as exc:
        logger.exception("UNHANDLED EXCEPTION")

        return JSONResponse(
            status_code=500,
            content={"error": str(exc)}
        )


@app.post("/upload_pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    try:
        logger.info(
            f"received file: {file.filename} "
            f"for session: {session_id}"
        )

        load_vectorstore(
            [file],
            session_id
        )

        logger.info("document added to chroma")

        return {
            "message": "File processed and vectorstore updated"
        }

    except Exception as e:
        logger.exception("Error during pdf upload")

        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/ask/")
async def ask_question(
    question: str = Form(...),
    session_id: str = Form(...)
):
    try:
        logger.info(f"user query: {question}")

        embed_model = get_embeddings()

        # Use this user's ChromaDB only
        from modules.load_vectorstore import get_session_dirs

        _, chroma_dir = get_session_dirs(session_id)

        vectorstore = Chroma(
            persist_directory=str(chroma_dir),
            embedding_function=embed_model
        )

        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 10}
        )

        chain = get_llm_chain(retriever)

        result = query_chain(chain, question)

        logger.info("query successful")

        return result

    except Exception as e:
        logger.exception("Error processing question")

        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.delete("/delete_pdf/")
async def delete_pdf(
    filename: str,
    session_id: str
):
    try:
        logger.info(
            f"Deleting file: {filename} "
            f"for session: {session_id}"
        )

        deleted_chunks = delete_document(
            filename,
            session_id
        )

        logger.info(
            f"Deleted {deleted_chunks} chunks for {filename}"
        )

        return {
            "message": f"{filename} deleted successfully",
            "deleted_chunks": deleted_chunks
        }

    except Exception as e:
        logger.exception("Error during PDF deletion")

        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/documents/")
async def get_documents(session_id: str):
    try:
        files = list_documents(session_id)

        return {
            "documents": files
        }

    except Exception as e:
        logger.exception("Error fetching documents")

        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/test")
async def test():
    return {
        "message": "Testing successful..."
    }