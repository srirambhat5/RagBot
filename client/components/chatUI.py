import streamlit as st

from utils.api import ask_question


def render_chat():

    st.subheader("💬 Chat with your documents")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(
            msg["content"]
        )

    user_input = st.chat_input(
        "Type your question here..."
    )

    if user_input:

        st.chat_message("user").markdown(user_input)

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        response = ask_question(
            user_input,
            st.session_state.session_id
        )

        if response.status_code == 200:

            data = response.json()

            answer = data["response"]
            sources = data.get("sources", [])

            st.chat_message("assistant").markdown(answer)

            if sources:
                st.markdown("📄 **Sources:**")

                for src in sources:
                    st.markdown(f"- `{src}`")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        elif response.status_code == 503:

            st.warning(
                "⚠️ Gemini is currently busy. "
                "Please try again in a few seconds."
            )

        else:

            st.error(
                "⚠️ Something went wrong while processing your question. "
                "Please try again."
            )