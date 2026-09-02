import streamlit as st

from utils.api import upload_pdfs_api, get_documents, delete_pdf


def render_uploader():

    st.sidebar.header("Upload PDFs")

    uploaded_files = st.sidebar.file_uploader(
        "Upload multiple PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    if st.sidebar.button("Upload to DB") and uploaded_files:

        responses = upload_pdfs_api(
            uploaded_files,
            st.session_state.session_id
        )

        if all(response.status_code == 200 for response in responses):
            st.sidebar.success("Uploaded successfully")
        else:
            for response in responses:
                if response.status_code != 200:
                    st.sidebar.error(
                        f"Error: {response.text}"
                    )

    st.sidebar.header("Uploaded Documents")

    response = get_documents(
        st.session_state.session_id
    )

    if response.status_code == 200:

        documents = response.json().get("documents", [])

        if documents:

            for filename in documents:

                col1, col2 = st.sidebar.columns([3, 0.8])

                col1.write(filename)

                if col2.button(
                    "🗑️",
                    key=f"delete_{filename}"
                ):

                    delete_response = delete_pdf(
                        filename,
                        st.session_state.session_id
                    )

                    if delete_response.status_code == 200:
                        st.rerun()
                    else:
                        st.sidebar.error(
                            f"Error deleting {filename}: "
                            f"{delete_response.text}"
                        )

        else:
            st.sidebar.write("No PDFs uploaded.")

    else:
        st.sidebar.error(
            "Could not fetch uploaded documents."
        )