# -*- coding: utf-8 -*-
import os
import openai
import streamlit as st
from acs_lib import *
from streamlit.web.server.websocket_headers import _get_websocket_headers

# ユーザー情報の取得
headers = _get_websocket_headers()
principal_name = headers.get("X-Ms-Client-Principal-Name")


# タイトルの設定
st.title("Answer with Data")

#OSの環境変数から読み込み
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_ENDPOINT_FQDN")

#OpenAIの設定
openai.api_type = "azure"                     #APITYPEの指定をAzure用に指定
openai.api_key = API_KEY                      #APIキーを指定
openai.api_base = RESOURCE_ENDPOINT         #アクセスエンドポイントを指定
openai.api_version = "2023-03-15-preview"     #適合するAPIバージョンを指定

with st.sidebar:
    if principal_name is not None:
        st.markdown('ようこそ ' + principal_name + 'さん')
    st.image("Demo2.png")
    st.subheader("Configuration")
    index = st.text_input("index select", value="idx-aoai-jp-1")
    st.text("idx-aoai-ads-001 : On Your Data\nidx-aoai-jp-1 : Vector Index")
    vector = st.checkbox("Vector", value=True)
    model = st.text_input("model select", value="gpt-4")

# acs_lib.py からインスタンスを作成
acs = ACS_CLASS(index)

# 使用するGPTモデルの設定
st.session_state["openai_model"] = model

# streamlit のセッション情報に messages が存在しない場合に作成
if "messages" not in st.session_state:
    st.session_state.messages = []
    # st.session_state.messages.append({"role": "system", "content": "ギャル語で話して"})

# messages から message をループで取り出し、systemロール以外を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "system":
            continue
        else:
            st.markdown(message["content"])

#
# プロンプト入力に伴う処理
# 
if prompt := st.chat_input("入力してください"):
    # 入力された promptを messages に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    # user ロールのメッセージを表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # Azure Cognitive Search に対して prompt で検索をかけ、結果を取得
    if(vector):
        acs_results = acs.search_vector_query(prompt)
    else:
        acs_results = acs.search_query(prompt)

    # system メッセージの作成
    system_message =f"""
    Answer the question as truthfully as possible using the provided text below, and if you're unsure of the answer, say Sorry, 'I don't know'. You must answer in Japanese.
    
    {acs_results[0]['content']}

    {acs_results[1]['content']}

    {acs_results[2]['content']}
    
    """

    # system メッセージを messages に追加
    st.session_state.messages.append({"role": "system", "content": system_message})

    # print(st.session_state)

    # GPTに messages を投げて結果を取得し表示
    with st.chat_message("assistant"):
        # GPTからの応答を保存する場所
        message_placeholder = st.empty()
        # 最終的なすべての応答を作るための変数
        full_response = ""
        for response in openai.ChatCompletion.create(
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
        dicdata0 = {
            'filepath': acs_results[0]['filepath'],
            'content': acs_results[0]['content'],
        }
        st.json(dicdata0)
        dicdata1 = {
            'filepath': acs_results[1]['filepath'],
            'content': acs_results[1]['content'],
        }
        st.json(dicdata1)
        dicdata2 = {
            'filepath': acs_results[2]['filepath'],
            'content': acs_results[2]['content'],
        }
        st.json(dicdata2)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

print(st.session_state)
