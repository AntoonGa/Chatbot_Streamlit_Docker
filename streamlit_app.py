import streamlit as st

from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

import chatbot_streamlit as chatbot_streamlit
import textwrap


# FUNCTION DEF #
def flush_conversation():
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


# def wrap_code(code: str, width: int = 80) -> str:
#     """
#     Wrap long lines of code to the specified width.

#     :param code: The code string to wrap.
#     :type code: str
#     :param width: The maximum width of a line, defaults to 80.
#     :type width: int, optional
#     :return: The wrapped code string.
#     :rtype: str
#     """
#     lines = code.split('\n')
#     wrapped_lines = []

#     for line in lines:
#         stripped_line = line.lstrip()
#         indent = len(line) - len(stripped_line)
#         wrapped_line = textwrap.wrap(stripped_line, width=width - indent, break_long_words=False)
#         wrapped_line = [f"{' ' * indent}{l}" if i ==
#                         0 else f"{' ' * (indent + 4)}{l}" for i, l in enumerate(wrapped_line)]
#         wrapped_lines.extend(wrapped_line)

#     wrapped_code = '\n'.join(wrapped_lines)
#     return wrapped_code
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
    lines = repr(code).split('\\n')
    wrapped_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        indent = len(line) - len(stripped_line)
        wrapped_line = textwrap.wrap(stripped_line, width=width - indent, break_long_words=False)
        wrapped_line = [f"{' ' * indent}{l}" if i ==
                        0 else f"{' ' * (indent + 4)}{l}" for i, l in enumerate(wrapped_line)]
        wrapped_lines.extend(wrapped_line)
    wrapped_code = '\n'.join(wrapped_lines)
    return wrapped_code

# Response output
# Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt, chatbot):  
    for yielded in st.session_state['chatbot'].send_receive_message(prompt):
        yield yielded

# User input
# Function for taking user provided prompt as input
def get_text():
    def clear_text():
        st.session_state["text"] = ""
        return 
          
    input_text = st.text_area("Input", key="text")
    st.button("clear text input", on_click=clear_text)
    st.write(input_text)
    
    return input_text


# STREAMLIT HANDLING
st.set_page_config(page_title="LLM Agent", layout="wide", initial_sidebar_state  = "expanded")

# machine state initalization
if 'chatbot' not in st.session_state:
    # instantiate chatbot
    st.session_state['chatbot'] = chatbot_streamlit.llm()
# generated stores AI generated responses
if 'generated' not in st.session_state:
    # instanciate the chatbot if the sesssion state is empty !
    st.session_state['generated'] = ["idx:0"]
# past stores User's questions
if 'past' not in st.session_state:
    st.session_state['past'] = ['idx:0']
# initialize last user input (usefull for some conditions)
if 'last_user_input' not in st.session_state:
    st.session_state['last_user_input'] = ''


# Sidebar contents
with st.sidebar:
    st.title("🤗💬 Antoine chatbot Features:")
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
        ('coder', 'commenter', 'chatbot', "dummy"))
    if 'chatbot' in st.session_state and st.session_state['chatbot'].system_function != option_system:
        st.session_state['chatbot'].set_system_function(option_system)
        st.write(st.session_state['chatbot'].system_function)

    add_vertical_space(2)
    if st.button('Flush memory'):
        if 'chatbot' in st.session_state:
            st.write('Flushed')  # displayed when the button is clicked
            flush_conversation()


# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='blue-30')
response_container = st.container()

# Applying the user input box
with input_container:
    user_input = get_text()

# Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    # get response only if there is a user_input and if it was different that the last one.
    if user_input and user_input != st.session_state['last_user_input']:
        # make sure we don't rerun the function if user_input has not changed
        st.session_state['last_user_input'] = user_input
        st.session_state.past.append(user_input)
        
        # horizontal line between chat sessions
        st.markdown("<hr/>", unsafe_allow_html=True)
        # this is where the streaming response will be appended
        st.session_state.generated.append("")
        # Create a single code_placeholder using st.empty()
        code_placeholder = st.empty()
        # stream the response
        for yielded in generate_response(user_input, st.session_state['chatbot']):
            st.session_state.generated[-1] = st.session_state.generated[-1] + yielded
            if st.session_state.generated[-1]:          
                try:
                    # preprocess message answer (wrap text to fit box width and set indentation)
                    wrap_generated = wrap_code(code=st.session_state["generated"][-1], width=80)
                    # display message as code
                    code_placeholder.code(wrap_generated, language='python', line_numbers =True)
                except:
                    pass
        wrap_past = wrap_code(code=st.session_state['past'][-1], width=80)
        # st.code(wrap_past, language='python')
        st.text(wrap_past)

        # display chathistory.
        if len(st.session_state['generated']) > 2:
            for i in range(len(st.session_state['generated'])-2,0,-1):
                # do not display the first "useless" messages!
                try:
                    # preprocess message answer (wrap text to fit box width and set indentation)
                    wrap_generated = wrap_code(code=st.session_state["generated"][i], width=80)
                    wrap_past = wrap_code(code=st.session_state['past'][i], width=80)
                    # display message as code
                    st.markdown("<hr/>", unsafe_allow_html=True)
                    st.code(wrap_generated, language='python', line_numbers =True)
                    # st.code(wrap_past, language='python')
                    st.text(wrap_past)

                except:
                    pass

