# 1 LLM Chatbot

A copilot chatbot with dynamic history management. The chatbot uses OpenAI's language models to provide responses to user queries. The history can be adjusted, flushed, or popped to manage the chatbot's memory.

## Features

- Initialize the chatbot with a specified language model engine and token limits
- Adjust the chat history size to ensure it does not exceed the maximum token context
- Flush the chat history, keeping only the initial system message
- Remove the oldest question and answer from the chat history
- Interact with the chatbot in a continuous loop
- Change the system function or engine during the chat

## Usage

1. Set up the required environment variables for OpenAI API keys in the `openia_config.txt` file.
2. Import the `llm` class and create a chatbot instance with the desired language model engine:

```python
from llm_chatbot import llm

chatbot = llm(llm_engine="gpt-4-32k")
```

3. Start the chat with the chatbot:

```python
chatbot.chat()
```

During the chat, you can use the following commands:

- `exit`: Stop the chat
- `flush`: Destroy the chat history, keeping the system function
- `pop`: Remove the oldest question and answer from the chat history, keeping the system function
- `system`: Destroy the chat history and reset the system function
- `engine`: Change the language model engine, keeping the system function and chat history

## Dependencies

- Python 3.6+
- `tiktoken`
- `openai`

# 2 Streamlit LLM Chatbot
## Code Overview
The code is organized into several functions and a Streamlit application layout.
### Functions
- `flush_conversation()`: Clears the chatbot's conversation history.
- `wrap_code(code: str, width: int = 80) -> str`: Wraps long lines of code to the specified width.
- `generate_response(prompt, chatbot)`: Takes a user prompt as input and produces an AI-generated
    response.
- `get_text()`: Takes user input as a prompt.
### Streamlit Application
The Streamlit application is organized into a sidebar and main content area. The sidebar contains
    options for selecting the chatbot's engine, system function, and a button to flush the chatbot's
    memory. The main content area displays the user input box and the conversation history.
## Usage
To run the Streamlit application, first install the required dependencies:
```
pip install streamlit streamlit_chat streamlit_extras
```
Then, run the Streamlit application:
```
streamlit run app.py
```
Open the provided URL in your browser to interact with the chatbot.

## License

This project is licensed under the MIT License.

## TDL
factorize streamlit code in object.
enable streaming mode to streamlit
enable changing llm on the fly (All Azure Models okay, add one from AWS -Hugging Face and a local llm)