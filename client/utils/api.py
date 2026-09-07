import requests

from config import API_URL


def upload_pdfs_api(files, session_id):

    responses = []

    for f in files:

        files_payload = {
            "file": (
                f.name,
                f.getvalue(),
                "application/pdf"
            )
        }

        response = requests.post(
            f"{API_URL}/upload_pdf/",
            files=files_payload,
            data={
                "session_id": session_id
            }
        )

        responses.append(response)

    return responses


def get_documents(session_id):

    return requests.get(
        f"{API_URL}/documents/",
        params={
            "session_id": session_id
        }
    )


def delete_pdf(filename, session_id):

    return requests.delete(
        f"{API_URL}/delete_pdf/",
        params={
            "filename": filename,
            "session_id": session_id
        }
    )


def ask_question(question, session_id):

    return requests.post(
        f"{API_URL}/ask/",
        data={
            "question": question,
            "session_id": session_id
        }
    )