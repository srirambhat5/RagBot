from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from logger import logger


app = FastAPI(
    title="RagBot2.0"
)


# ---------------- CORS ---------------- #

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------------- Global Exception Handler ---------------- #

@app.middleware("http")
async def catch_exception_middleware(
    request: Request,
    call_next
):

    try:

        return await call_next(request)

    except Exception as exc:

        logger.exception(
            "UNHANDLED EXCEPTION"
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc)
            }
        )


# ---------------- Upload PDF ---------------- #

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

        from modules.load_vectorstore import (
            load_vectorstore
        )

        load_vectorstore(
            [file],
            session_id
        )

        logger.info(
            "document added to chroma"
        )

        return {
            "message":
                "File processed and vectorstore updated"
        }

    except ValueError as e:

        # Duplicate filename
        logger.warning(
            f"Upload rejected: {e}"
        )

        return JSONResponse(
            status_code=409,
            content={
                "error": str(e)
            }
        )

    except Exception as e:

        logger.exception(
            "Error during pdf upload"
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# ---------------- Ask Question ---------------- #

@app.post("/ask/")
async def ask_question(
    question: str = Form(...),
    session_id: str = Form(...)
):

    try:

        logger.info(
            f"user query: {question}"
        )

        from modules.load_vectorstore import (
            get_embeddings,
            get_session_dirs
        )

        from modules.llm import (
            get_llm_chain
        )

        from modules.query_handlers import (
            query_chain
        )

        from langchain_chroma import (
            Chroma
        )

        embed_model = get_embeddings()

        _, chroma_dir = get_session_dirs(
            session_id
        )

        vectorstore = Chroma(
            persist_directory=str(chroma_dir),
            embedding_function=embed_model
        )

        retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 10
            }
        )

        chain = get_llm_chain(
            retriever
        )

        result = query_chain(
            chain,
            question
        )

        logger.info(
            "query successful"
        )

        return result

    except Exception as e:

        logger.exception(
            "Error processing question"
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# ---------------- Delete PDF ---------------- #

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

        from modules.load_vectorstore import (
            delete_document
        )

        deleted_chunks = delete_document(
            filename,
            session_id
        )

        logger.info(
            f"Deleted {deleted_chunks} chunks "
            f"for {filename}"
        )

        return {
            "message":
                f"{filename} deleted successfully",
            "deleted_chunks":
                deleted_chunks
        }

    except Exception as e:

        logger.exception(
            "Error during PDF deletion"
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# ---------------- List Documents ---------------- #

@app.get("/documents/")
async def get_documents(
    session_id: str
):

    try:

        from modules.load_vectorstore import (
            list_documents
        )

        files = list_documents(
            session_id
        )

        return {
            "documents": files
        }

    except Exception as e:

        logger.exception(
            "Error fetching documents"
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# ---------------- Test ---------------- #

@app.get("/test")
async def test():

    return {
        "message":
            "Testing successful..."
    }