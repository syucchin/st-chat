# -*- coding: utf-8 -*-
import os
import openai
import streamlit as st
from acs_lib import *

st.title("ChatGPT-like clone")

#OS環境変数からキーを入手する
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_ENDPOINT_FQDN")

#OpenAI上必要な変数設定を実装する
openai.api_type = "azure"                     #APITYPEの指定をAzure用に指定
openai.api_key = API_KEY                      #APIキーを指定
openai.api_base = RESOURCE_ENDPOINT         #アクセスエンドポイントを指定
openai.api_version = "2023-03-15-preview"     #適合するAPIバージョンを指定

acs = ACS_CLASS()

if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"
    st.session_state["openai_model"] = "gpt-4"

if "messages" not in st.session_state:
    st.session_state.messages = []
    # st.session_state.messages.append({"role": "system", "content": "ギャル語で話して"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "system":
            continue
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("入力してください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    acs_results = acs.search_vector_query(prompt)

    system_message =f"""
    Answer the question as truthfully as possible using the provided text below, and if you're unsure of the answer, say Sorry, 'I don't know'. You must answer in Japanese.
    
    {acs_results[0]['content']}

    {acs_results[1]['content']}

    {acs_results[2]['content']}
    
    """
    # print(system_message)

    st.session_state.messages.append({"role": "system", "content": system_message})

    print(st.session_state)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            # model = st.session_state["openai_model"],
            engine = st.session_state["openai_model"],
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
        ):
            if len(response.choices) > 0:
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            else:
                print("No response generated")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

print(st.session_state)
