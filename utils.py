import streamlit as st
from openai import OpenAI
import time
import PyPDF2
from docx import Document
import re


openai_api_key = st.secrets['api_keys']['OPENAI_API_KEY']
client = OpenAI(api_key=openai_api_key)

assistant_id = st.secrets['api_keys']["ASSISTANT_ID"]


def perform_openai_api_processing(user_input):
    try:
        thread = client.beta.threads.create()
        llm_response, run = submit_message(user_input, thread)

        run = wait_for_run(thread, run)

        text = ""
        # Step 5: Check the run status and return the assistant's response
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            llm_response = messages.data[0]
            text = llm_response.content[0].text.value  # Extract response text
            text = re.sub(r"\[\d+\]", "", text)

            return {"message": text}

        elif run.status == "requires_action":
            return {"message": "The assistant requires further actions or tool invocations."}
    except Exception as e:
        return {"message": f"Invalid request method: {e}", "status": 400}

    return text


def submit_message(content, thread):
    """
        Creates a message and initiates an asynchronous 'run' command
        :param assistant_id: ID code for the GPT Assistant API
            :param content: The message content to send (e.g. the disclosure case)
            :param thread: The thread object related to this message instance.
            :return: (message, run): references to the message and the run objects.
            """
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    return message, run


def wait_for_run(thread, run):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)

    return run


def read_uploaded_file(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        return content
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        content = "\n".join([para.text for para in doc.paragraphs])
        return content
    else:
        return "Unsupported file type"