# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 12:56:21 2023

@author: agarc
"""
# imports
import time
import traceback
import logging
import tiktoken
import openai

# set path for API config
import os
main_path = './'
keys_path = os.path.join(main_path, 'openia_config.txt')
keys_file = open(keys_path)
lines = keys_file.readlines()
keys_file.close()
# Set API keys
openai.api_type = lines[0].split("=")[1].strip()
openai.api_base = lines[1].split("=")[1].strip()
openai.api_version = lines[2].split("=")[1].strip()
openai.api_key = lines[3].split("=")[1].strip()


class llm():
    """
    A copilot chatbot. History is dynamic (pops when too long, can be deleted)
    """

    def __init__(self):
        """
        Initialize the Chatbot instance with the specified language model engine and token limits.

        This function sets the system function, engine model, and token limits based on the provided engine name.
        It also calculates the maximum token context to avoid overfeeding tokens.

        Args:
            self: The Chatbot instance.
            llm_engine (str, optional): The name of the language model engine to use. Defaults to "gpt-4-32k".

        Returns:
            None
        """

        # initiate system function
        self.set_system_function("coder")
        # set system model and context length according to chosen model
        self.set_engine('gpt4')
        
        print("---")
        print("INIT IS DONE")
        print("---")
        return

    ### USER FUNCTION ###

    def send_receive_message(self, user_query=""):
        """
        Send a single message using history as payload and append the response to the history.

        This function sends the full history as payload, receives the response from the language model, and appends
        the response to the chat history. The history is used for debugging and monitoring purposes.

        Args:
            self: The Chatbot instance.
            query (str): The message to send to the language model.

        Returns:
            str: The response from the language model.
        """
        # if no message is provided, we set a default one
        if len(user_query) <= 0:
            response = "Please provide a question."

        else:
            print("------------------------")
            print("Query: \n")
            print(user_query)
            print('Answer: \n')
            # append history with user query
            self._append_history(role="user", content=user_query)
            # remove part of history (first after system) if history is too long
            self._adjust_history_size()
            # send full history has payload
            payload = self.history
            # send history to llm and get response
            response = ''
            for yielded in self._send_payload_stream_answer(payload):
                response = response + yielded
                yield yielded
            # append history with system message
            self._append_history(role="assistant", content=response)
        return response

    def set_engine(self, user_input='gpt4'):
        """
        Set the engine and its corresponding token limits based on the selected engine.

        This function sets the engine, maximum tokens allowed in the context, and maximum tokens allowed in the response
        based on the selected engine. It also calculates the maximum token context by subtracting the response tokens
        and a buffer token value from the total maximum tokens.

        Args:
            self: An instance of the class containing the engine and token attributes.

        Returns:
            None
        """
        # add to this dictionnaries different engine that the system can take:)
        hardcoded_engines = {"gpt4": "gpt-4-32k",
                             "gpt3": "gpt-35-turbo"}
        
        # if the engine is hardcoded, else we use gpt4
        if user_input in hardcoded_engines:
            self.engine = hardcoded_engines[user_input]
        else:
            self.engine = hardcoded_engines['gpt4']

        # set tokens memory of the engine
        if self.engine == "gpt-4-32k":  # this model is rather expensive !
            self.max_tokens = 30000  # maximum token in llm context
            self.max_tokens_in_response = 4000  # maximum token in llm response
        elif self.engine == "gpt-35-turbo":
            self.max_tokens = 8000
            self.max_tokens_in_response = 2000  # maximum token in llm response
            

        buffer_token = 1000  # avoid over feeding tokens, note that the prompt template needs some tokens !
        self.max_token_context = self.max_tokens - self.max_tokens_in_response - buffer_token  # rest

        print("Engine:", self.engine)
        return 

    def set_system_function(self, user_input="coder"):
        """
        Initialize the chatbot's system function and set it as the first entry in the chat history.      

        Args:
            self: The Chatbot instance.

        Returns:
            None
        """
        # add to this dictionnaries different roles that the system can take:)
        hardcoded_systems = {"commenter": """
        I will provide python functions. 
        You will provide description headers for these functions. Be concisce. 
        First interpret what the function do. Then write a short description of the function. 
        Next in the header write what the arguement and outputs are in the pythonic triple quote format.
        Also add comment to lines of code that are complicated or use external libraries
        """,
                             "coder": """
        You are a coding assistant for Python developpers. A Python co-pilot !
        You are consice, precice and code at the highest level.
        You use a wide variety of famous Python package and library.
        You provide codes with good comments and functions headers indicating the types of output and arguments.
        When you provide code, make sur it is well delimited from your other sentenses.
        """,
                             "chatbot": """
        You are a helpfull assistant.
        You provide accurate answer to users queries.
        """,
                            "dummy": """
       We will play a game you and me.
       You will be a very very stupid IA that believe stupid things.
       I will ask question and you will answer idiotic things. :)
       """}

        if user_input in hardcoded_systems:
            self.system_function = hardcoded_systems[user_input]
        else:
            self.system_function = user_input

        # init the system on call
        role_system = {'role': 'system', 'content': self.system_function}
        # change the system function if it exists
        try:
            self.history[0] = role_system
        except:
            # of create the history if it does not exists.
            self.history = [role_system]

        print("System function:", self.system_function)
        return 

    def flush_history(self):
        """
        Flush the chat history, keeping only the initial system message.
        This function removes all elements from the chat history except the first one, which is the initial system message.
        """
        self.history = [self.history[0]]
        return


    ### internal use function ###
    
    def _count_tokens(self, encoding_name="cl100k_base"):
        """
        Calculate the total number of tokens in the chat history.
        Generates a full string from the chat history
        Computes the number of tokens using the specified encoding model, and adds the number of keys from the history to the context length.

        Args:
            encoding_name (str, optional): The name of the encoding model to use. Defaults to "cl100k_base".

        Returns:
            int: The total number of tokens in the chat history.
        """
        # generate full string from history
        string_total = ''.join([chat["content"] for chat in self.history])
        # compute number of tokens tokens
        encoding = tiktoken.encoding_for_model("gpt-4")
        num_tokens = len(encoding.encode(string_total))
        # add the keys from history in the context length
        num_tokens += len(self.history)
        return num_tokens

    def _adjust_history_size(self):
        """
        Adjust the chat history size to ensure it does not exceed the maximum token context.

        This function calculates the number of tokens in the chat history and reduces the context size if needed by
        removing the oldest elements until the history size is within the allowed limit.
        """
        # assign first number to enter the while loop
        number_of_tokens_in_history = self._count_tokens()
        # reduce context if needed
        if number_of_tokens_in_history >= self.max_token_context:
            # in a while loop, until the history is of appropriate size
            while number_of_tokens_in_history >= self.max_token_context:
                print("\n ----- max context size reached. Poping. ----- \n")
                # remove the element after the system message (oldest element)
                self._pop_history()
                # count again
                number_of_tokens_in_history = self._count_tokens()
        return

    def _send_payload_stream_answer(self, payload):
        """
        Send the payload to the OpenAI API and stream the response, handling timeouts and retries.

        This function sends the payload to the OpenAI API using the ChatCompletion.create method with streaming enabled.
        It handles timeouts and retries up to 3 times before returning the response.

        Args:
            self: The Chatbot instance.
            payload (dict): The payload to send to the OpenAI API.

        Returns:
            str: The response from the OpenAI API.
        """
        time.sleep(0.5)
        # we make multiple tries with a 10second timeout
        is_to_do = 1  # break condition 1
        try_counter = 0  # break contition 2: will break if number of attempts is 5
        while is_to_do == 1 and try_counter <= 3:
            try:
                for chunk in openai.ChatCompletion.create(
                        engine=self.engine,
                        temperature=0,
                        max_tokens=self.max_tokens_in_response,
                        messages=payload,
                        stream=True,
                        timeout=10):
                    content = chunk["choices"][0].get("delta", {}).get("content")
                    if content is not None:
                        print(content, end='')
                        yield content

                is_to_do = 0

            except Exception as e:
                logging.error(traceback.format_exc())
                print("Timeout. Retry:", try_counter)
                try_counter += 1
                time.sleep(1)

        return

    def _pop_history(self):
        """
        Remove the oldest question and answer from the chat history.
        """
        try:
            self.history.pop(1)
            self.history.pop(1)
        except Exception as e:
            logging.error('Failed to remove second element of history: ' + str(e))
        return

    def _append_history(self, role, content):
        """
        Append a new message to the chat history.
        This function adds a new message to the chat history with the specified role and content.

        Args:
            role (str): The role of the message sender, e.g., "user" or "assistant".
            content (str): The content of the message.

        Returns:
            None
        """
        # place new user message in history
        new_message = {"role": role, "content": content}
        self.history.append(new_message)
        return


# %%
def main():
    chatbot = llm()
    chatbot.set_engine("gpt3")
    chatbot.set_engine("gpt4")

    chatbot.set_system_function("coder")

    chatbot.send_receive_message()

    query = "What's the fastest between pandas and spark"
    response = ''
    for yielded in chatbot.send_receive_message(query):
        response = response + yielded

    print('\n--\n')
    print(response)
if __name__ == "__main__":
    main()
