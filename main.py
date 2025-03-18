import streamlit as st
from utils import *


def get_complexity_details(slider_value):
    instructions = ""

    # For public audience (layman)
    if 0 < slider_value <= 3:
        instructions = (
            "Make the responses simple and easy to understand, using plain language and minimal technical terms. "
            "Assume the audience has no prior knowledge of the subject matter."
        )
    # For mixed audience (layman and professionals)
    elif 4 <= slider_value <= 7:
        instructions = (
            "Make the response clear and accessible to both a layman and a professional lawyer. "
            "Use a balanced level of technical language that explains complex concepts "
            "without overwhelming the layperson, "
            "while still being understandable to professionals."
        )
    # For professional lawyers
    elif slider_value > 7:
        instructions = (
            "Make the response highly professional and sophisticated, tailored for legal professionals. "
            "Use precise legal language and include any necessary technical terms that a "
            "lawyer would understand and find useful for their work."
        )

    return instructions


if __name__ == "__main__":
    st.title("Chat with Dada Wakili")

    st.sidebar.title("Model Responses")
    slider_value = st.sidebar.slider("Response complexity", min_value=0, max_value=10, value=5)
    st.write(f"Response Complexity : {slider_value}")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.sidebar.title("Supported Features")

    instruction = get_complexity_details(slider_value)
    use_case = ""

    uploaded_file = st.sidebar.file_uploader("Upload a document", type=["txt", "pdf", "docx"])

    checkbox_legal_research = st.sidebar.checkbox("Legal Research")
    checkbox_thematic_analysis = st.sidebar.checkbox("Thematic Analysis")
    checkbox_summarise_document = st.sidebar.checkbox("Summarise Document")
    checkbox_validate_document = st.sidebar.checkbox("Validate Document")
    checkbox_explain_clause = st.sidebar.checkbox("Explain a Clause")

    # Store chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    prompt_fine_tune = ""

    if checkbox_legal_research or checkbox_thematic_analysis or checkbox_summarise_document or checkbox_validate_document or checkbox_explain_clause:
        if uploaded_file is None:
            st.warning("Please upload a file")

    if uploaded_file is not None:
        file_content = read_uploaded_file(uploaded_file)
        if checkbox_legal_research:
            prompt_fine_tune = \
                f"You are a researcher. Analyse the attached document based on the uploaded files " \
                f"and on what you know. Return valid, well-thought-out responses. " \
                f"{instruction}" \
                f"The uploaded file's content is: {file_content}."
            use_case = "Research initiated ..."
        elif checkbox_thematic_analysis:
            prompt_fine_tune = \
                f"Perform an in-depth thematic analysis of the uploaded document." \
                f"{instruction}" \
                f" The uploaded file's content is: {file_content}"
            use_case = "Thematic analysis initiated ..."
        elif checkbox_summarise_document:
            use_case = "Text summarization initiated ... "
            prompt_fine_tune = f"Summarise the uploaded document. " \
                               f"{instruction}" \
                               f"The uploaded file's content is: {file_content}"
        elif checkbox_validate_document:
            use_case = "Document validation initiated ..."
            prompt_fine_tune = f"Validate the uploaded document. " \
                               f"{instruction}" \
                               f"The uploaded file's content is: {file_content}"
        elif checkbox_explain_clause:
            use_case = "Legal clauses explanation initiated ... "
            prompt_fine_tune = f"Explain all legal clauses in the uploaded document." \
                               f"{instruction}" \
                               f" Ignore any clauses that are non-legal. The uploaded file's content is: {file_content}"

    if use_case != "":
        st.write(use_case)

    # Display chat history
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

    # User input
    if user_input := st.chat_input("Type your message..."):
        # Add user message to session state
        st.session_state["messages"].append({"role": "user", "text": user_input})

        # Refresh UI to show user message before bot response
        st.rerun()

    # Check if the last message was from the user and bot has not responded
    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
        user_input = st.session_state["messages"][-1]["text"]

        # Send message to Rasa and get response
        final_input = prompt_fine_tune + " " + user_input

        response = perform_openai_api_processing(user_input)

        if response != "":
            bot_responses = response["message"]

            if bot_responses:
                # Create an empty placeholder for the bot's response
                response_placeholder = st.empty()

                # Add the bot's message to the session state incrementally
                full_response = ""
                is_first_line = True
                for word in bot_responses.split():
                    full_response += word + " "
                    response_placeholder.markdown(full_response.strip())
                    time.sleep(0.1)  # Simulate a delay for streaming effect

                # Once complete, finalize the message
                st.session_state["messages"].append({"role": "assistant", "text": bot_responses})

            # Refresh UI to display bot response
            st.rerun()