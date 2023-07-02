# LLM Chatbot

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

## License

This project is licensed under the MIT License.