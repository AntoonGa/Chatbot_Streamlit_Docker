# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 12:56:21 2023

@author: agarc
TODO:
- currently, the loader only accepts files inside the working directory.
This is an issue with streamlit which only remembers filenames and not path (its a security thing)
So pass the text files I will probably have to load the files/text using streamlit and pass the string to the backend.
I would rather have the backend do the loading but Im not sure its possible... 
- test for stability. Sometime the system hangs, I cannot explain why yet.
- text display gets it wrong when there is html stuff (' and \ and -)
- error handling
- make sure the backend does get the docstring (this one) at the beginning of the file.
- code factoring. Streamlit is a mess
- display user question in mini text could be usefull
- a button to download history json
- add docstrings to each functions.
"""
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import chatbot_streamlit as chatbot_streamlit
import textwrap
from tempfile import NamedTemporaryFile
import re

# FUNCTION DEF #
def flush_conversation():
    """
    Flush the conversation history in the Streamlit session state.
    This function clears the generated responses, past user inputs, and chatbot history.
    Everything happens in the llm backend
    """
    try:
        st.session_state['generated'] = [st.session_state['generated'][0]]
    except:
        pass

    try:
        st.session_state['past'] = [st.session_state['past'][0]]
    except:
        pass

    try:
        st.session_state['chatbot'].flush_history()
    except:
        pass
    return

def separate_text_and_code(text: str) -> tuple:
    """
    Separates text and Python code from a string containing text and code
        enclosed by "```python" and "```".
    :param text: str, the input string containing text and code
    :return: tuple, a tuple containing two lists:
             1. A list of text and code segments in chronological order
             2. A list of metadata indicating whether the corresponding element
                 in the first list is code or text
    """
    pattern = r'(.*?)```python(.*?)```'
    segments = []
    metadata = []
    for match in re.finditer(pattern, text, re.DOTALL):
        text_segment, code_segment = match.groups()
        segments.append(text_segment.strip())
        metadata.append("text")
        segments.append(code_segment.strip())
        metadata.append("code")
    # if no segment is found we can exist the function
    if not segments:
        return [text], ["text"]
    # Append the remaining text after the last code block
    last_code_end = text.rfind("```")
    if last_code_end != -1:
        segments.append(text[last_code_end + 3:].strip())
        metadata.append("text")
    return segments, metadata


def wrap_code(code: str, width: int = 80) -> str:
    """
    Wrap long lines of code to the specified width.
    :param code: The code string to wrap.
    :type code: str
    :param width: The maximum width of a line, defaults to 80.
    :type width: int, optional
    :return: The wrapped code string.
    :rtype: str
    """
    # lines = repr(code).split('\\n')
    lines = code.split('\n')  # Changed from repr(code).split(\'\\\\')
    wrapped_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        indent = len(line) - len(stripped_line)
        wrapped_line = textwrap.wrap(stripped_line, width=width - indent, break_long_words=False)
        wrapped_line = [f"{' ' * indent}{l}" if i == 0 else f"{' ' * (indent + 4)}{l}" for i, l in enumerate(wrapped_line)]
        wrapped_lines.extend(wrapped_line)
    wrapped_code = '\n'.join(wrapped_lines)
    return wrapped_code

def wrap_text(text: str, width: int = 80) -> str:
    """
    Wrap the given text to the specified width.
    :param text: str, the input text to wrap
    :param width: int, optional, the maximum width of a line, defaults to 80
    :return: str, the wrapped text
    /!\ sometimes html stuff gets wrongs (wrong linebrakes)
    """
    # text = html.escape(text)
    wrapped_text = textwrap.fill(text, width=width, replace_whitespace=False)
    return wrapped_text

# Response output
# Function for taking user prompt as input followed by producing AI generated responses
# @st.cache_data
def generate_response(prompt, _chatbot): 
    """
    Generate a response from the chatbot based on the given prompt.
    :param prompt: str, the user input prompt
    :param _chatbot: chatbot_streamlit.llm instance, the chatbot object
    :return: str, the generated response from the chatbot
    The system can yield (backend), currently not usefull in the streamlit
    """
    response = ''
    for yielded in st.session_state['chatbot'].send_receive_message(prompt):
        response = response + yielded
        yield yielded
    return response

# User input
# Function for taking user provided prompt as input
def get_text():
    """
    Display a text area for user input and a button to clear the text area.
    :return: str, the user input text
    """
    def clear_text():
        st.session_state["text"] = ""
        return 
          
    input_text = st.text_area("Input", key="text")
    st.button("clear text input", on_click=clear_text)
    st.write(input_text)
    
    return input_text

def line_divider():
    """Stupid function to draw a line because I cant get it to work."""
    line = ["_" for ii in range(80)]
    
    return ''.join(line)

def update_context_tokens_display():
    """
    Update the display of context tokens in the Streamlit sidebar.
    This function calculates the number of context tokens in the chatbot's history
    and updates the display in the sidebar. (computation is in backend)
    """
    context_tokens = st.session_state['chatbot']._count_tokens_in_history()
    context_tokens_placeholder.write(f"Context tokens: {context_tokens}")


# STREAMLIT HANDLING
st.set_page_config(page_title="LLM Agent", layout="wide", initial_sidebar_state  = "expanded")

# machine state initalization
if "init" not in st.session_state:
    st.session_state['init'] = True
    st.experimental_rerun()
else:
    st.session_state.init = False
if 'chatbot' not in st.session_state:
    # instantiate chatbot
    st.session_state['chatbot'] = chatbot_streamlit.llm()
# generated stores AI generated responses
if 'generated' not in st.session_state:
    # instanciate the chatbot if the sesssion state is empty !
    st.session_state['generated'] = [""]
# past stores User's questions
if 'past' not in st.session_state:
    st.session_state['past'] = [""]
# initialize last user input (usefull for some conditions)
if 'last_user_input' not in st.session_state:
    st.session_state['last_user_input'] = ''
 


# Sidebar contents
with st.sidebar:
    st.title("🤗💬 Antoine chatbot Features:")
    
    context_tokens_placeholder = st.empty()

        
    add_vertical_space(2)
    option_engine = st.selectbox(
        'Engine',
        ('gpt4', 'gpt3'))
    if 'chatbot' in st.session_state and st.session_state['chatbot'].engine != option_engine:
        st.session_state['chatbot'].set_engine(option_engine)
        st.write(st.session_state['chatbot'].engine)

    add_vertical_space(2)
    option_system = st.selectbox(
        'System function',
        ('coder', 'commenter', 'chatbot', "dummy", "Python copilot"))
    if 'chatbot' in st.session_state and st.session_state['chatbot'].system_function != option_system:
        st.session_state['chatbot'].set_system_function(option_system)
        st.write(st.session_state['chatbot'].system_function) 
        
    add_vertical_space(2)
    if st.button('Flush memory'):
        if 'chatbot' in st.session_state:
            st.write('Flushed')  # displayed when the button is clicked
            flush_conversation()
            
    # uploader. This makes a list of paths to load.
    uploaded_files = st.file_uploader("File upload", type='py', accept_multiple_files= True)    
    if uploaded_files:
        full_paths = []
        st.session_state["file_paths"] = []
        for uploaded_file in uploaded_files:
            with NamedTemporaryFile(dir='.', suffix='.py') as f:
                f.write(uploaded_file.getbuffer())
                path = f.name.split('\\')
                path.pop(-1)
                full_path = '\\'.join(path) + '\\' + uploaded_file.name
                
                if full_path not in full_paths:
                    full_paths.append(full_path)
                
        st.session_state["file_paths"] = full_paths
    else:
        st.session_state["file_paths"] = []

    # send the file_paths to the chatbot. This appends in the main loop and is always updated
    if st.session_state['chatbot'].system_role == "Python copilot":
        if "file_paths" in st.session_state:
            st.session_state['chatbot'].add_context_py_file(st.session_state["file_paths"])
            print(*st.session_state["file_paths"])  
  
         



# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='blue-30')
response_container = st.container()

# Applying the user input box
with input_container:
    user_input = get_text()


# Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input and user_input != st.session_state['last_user_input']:
        
        
        # append a new instance of user question and answer
        st.session_state["generated"].append("")
        st.session_state['past'].append(user_input)
        
        #get the chatbot response and place in st.session_state["generated"]
        response_generator = generate_response(user_input, st.session_state['chatbot'])
        st.session_state["generated"][-1] = ''.join(response_generator) 
        
        #create empty response_placeholders
        response_placeholders = []
        for _ in range(len(st.session_state["generated"])):
            response_placeholders.append(st.empty())
            

        #read chatbot messages and display in REVERSE order
        nb_of_exchanges = len(st.session_state["generated"])
        for ii in range(0, nb_of_exchanges):
            # select the last response
            response_to_print = st.session_state["generated"][ii]
            # display algorithm
            if response_to_print:
                try:
                    # separate text from code
                    segments, metadata = separate_text_and_code(response_to_print)
                    # prepare the response as an empty string
                    response_content = ""
                    for idx, segment in enumerate(segments):
                        # if segment is code we display as 
                        if metadata[idx] == "code":
                            # regex to find the code ```python <code> ```
                            response_content += f"```python\n{segment.strip()}\n```\n"
                        else:
                            # if text we just wrap it
                            wrapped_text = wrap_text(segment.strip())
                            response_content += f"{wrapped_text}\n"
                    # Add horizontal line to separate chatbot responses displays
                    response_content += line_divider()
                    #display last response
                    response_placeholders[nb_of_exchanges-ii-1].markdown(response_content)
                    
                except:
                    pass
            else:
                pass
            
        # save the new user input for the if statement
        st.session_state['last_user_input'] = user_input

#update tokens context count
update_context_tokens_display()

#%%
