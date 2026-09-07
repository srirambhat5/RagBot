import streamlit as st

from utils.api import upload_pdfs_api, get_documents, delete_pdf


def render_uploader():

    st.sidebar.header("Upload PDFs")

    # --------------------------------------------------
    # Uploader version
    # --------------------------------------------------

    if "upload_version" not in st.session_state:
        st.session_state.upload_version = 0

    uploader_key = f"pdf_uploader_{st.session_state.upload_version}"

    uploaded_files = st.sidebar.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key=uploader_key
    )

    # --------------------------------------------------
    # Upload button
    # --------------------------------------------------

    if st.sidebar.button("Upload to DB", key="upload_to_db"):

        if not uploaded_files:

            st.sidebar.warning(
                "Please select at least one PDF."
            )

        else:

            responses = upload_pdfs_api(
                uploaded_files,
                st.session_state.session_id
            )

            all_success = True

            for file, response in zip(
                uploaded_files,
                responses
            ):

                if response.status_code == 200:
                    continue

                all_success = False

                if response.status_code == 409:

                    st.sidebar.warning(
                        f"📄 {file.name} is already uploaded."
                    )

                    st.sidebar.info(
                        "Delete the existing document below "
                        "if you want to upload a new version."
                    )

                else:

                    try:
                        error_message = response.json().get(
                            "error",
                            "Unknown error"
                        )
                    except Exception:
                        error_message = "Unknown error"

                    st.sidebar.error(
                        f"❌ Could not upload {file.name}: "
                        f"{error_message}"
                    )

            # --------------------------------------------------
            # SUCCESS
            # --------------------------------------------------

            if all_success:

                st.session_state.upload_version += 1

                st.sidebar.success(
                    "✅ All PDFs uploaded successfully!"
                )

                # Force Streamlit to create a completely
                # new uploader widget.
                st.rerun()

    # --------------------------------------------------
    # Uploaded Documents
    # --------------------------------------------------

    st.sidebar.header("Uploaded Documents")

    response = get_documents(
        st.session_state.session_id
    )

    if response.status_code == 200:

        documents = response.json().get(
            "documents",
            []
        )

        if documents:

            for filename in documents:

                col1, col2 = st.sidebar.columns(
                    [3, 0.8]
                )

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
                            f"Could not delete {filename}."
                        )

        else:

            st.sidebar.write(
                "No PDFs uploaded."
            )

    else:

        st.sidebar.error(
            "Could not fetch uploaded documents."
        )

