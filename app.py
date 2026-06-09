import streamlit as st
import re
from google import genai

print(st.__version__)
print(hasattr(st, "text_area"))
print(type(st.text_area) if hasattr(st, "text_area") else "missing")

st.title("Programmer Assistant")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Nerastas GEMINI_API_KEY. Įdėk API raktą į .streamlit/secrets.toml failą.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "gemini-2.5-flash"

AI_INFO = r"""
Role: You are a Python coding assistant

Functions:
1. If the user sends you a code with a problem or asks to append or polish something about the code then you mustn't delete the code and make a new one, you take the code that was given with the exact same structure (try your hardest to maintain the structure) and only polish the parts needed or add new things, fix them etc.
2. If the user asks you to create a code from scratch, well do exactly that! Create the code as best as you can according to the user's description/wishes.

Requirements/Restrictions:
1. You can only work with Python code and nothing else.
2. You must explain anything that you added/changed and give detailed explanation to how it works or why it's best.
3. You must post the code in the correct spacing and formating and it should be able to be simply pasted into a coding program and it has to work immediatly (Take note! Your code may be putted to testing through a simulated python instance so make sure the code is able to be pasted in no problems!)
4. When you write the code itself start it with: ./ and end it with \. (NOTE ./ HAS TO STRICTLTY BE PUT BEFORE THE FIRST LINE OF CODE NOT THE START OF THE PROMPT AND \. HAS TTO BE PUTTEN AFTER THE LAST LINE OF CODE!!!!)
"""

ReferanceCode = st.text_area("Type in the code you wish to be corrected/adjusted!", height=200)

code_placeholder_subheader = st.empty()
code_placeholder = st.empty()


if ReferanceCode:
    code_placeholder_subheader.subheader("This is the current version of your code:")
    code_placeholder.code(ReferanceCode, language="python")
else:
    code_placeholder.write("Your code preview will appear here.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("Type your message here..."):
    
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    AI_PROMPT = f"""
    {AI_INFO}
    
    CRITICAL CONTEXT:
    - Code provided by user in the text area: {ReferanceCode if ReferanceCode else "None"}
    - Chat History so far: {st.session_state.messages}
    
    LATEST USER REQUEST: 
    {user_prompt}
    
    Answer strictly according to the rules and roles provided above.
    """
    
    with st.chat_message("model"):
        with st.spinner("Generating your code!"):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=AI_PROMPT
                )
                ai_answer = response.text        
                st.markdown(ai_answer)
                
                pattern = r"\./(.*?)\\"
                match = re.search(pattern, ai_answer, re.DOTALL)
                if match:
                    extracted_code = match.group(1)
                    ReferanceCode = extracted_code
                    code_placeholder.code(extracted_code, language="python")
                
                
                
                st.session_state.messages.append({"role": "model", "content": ai_answer})

            except Exception as e:
                st.error("Atsiprašome, šiuo metu nepavyko sugeneruoti atsakymo.")
                st.exception(e)