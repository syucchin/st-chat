# -*- coding: utf-8 -*-
import os
import openai
import json
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureCliCredential
from azure.search.documents.models import Vector
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchField,
    SearchableField,
    SearchFieldDataType,
    SearchIndexer,
    IndexingParameters,
    FieldMapping,
    FieldMappingFunction,
    InputFieldMappingEntry, 
    OutputFieldMappingEntry, 
    SearchIndexerSkillset,
    SearchIndexerKnowledgeStore,
    SearchIndexerKnowledgeStoreProjection,
    SearchIndexerKnowledgeStoreFileProjectionSelector,
    IndexingParameters, 
    WebApiSkill,
    SearchIndex,
    SemanticSettings,
    SemanticConfiguration,
    PrioritizedFields,
    SemanticField,
    VectorSearch,  
    VectorSearchAlgorithmConfiguration
        )

#OS環境変数からキーを入手する
OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT_FQDN")

# ACS Integration Settings
SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE")
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
# SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX")

class ACS_CLASS:

    # クラスの初期化
    def __init__(self,index):
        openai.api_type = 'azure'
        openai.api_base = RESOURCE_ENDPOINT
        openai.api_key = OPENAI_KEY
        openai.api_version = '2023-06-01-preview'
        search_endpoint = SEARCH_ENDPOINT
        search_index = index
        search_key = SEARCH_KEY
        self.search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=search_index,
                credential=AzureKeyCredential(str(search_key)),
                )
        return

    def openaiEmbd(self,text: str):
        response = openai.Embedding.create(
                input = text,
                engine = "text-embedding-ada-002"
            )
        embeddings = response['data'][0]['embedding']
        return embeddings

    def search_query(self,request_msg):
        self.search_results = self.search_client.search(
            search_text=request_msg,
            top=5
        )
        results = []
        i = 0
        for search_result in self.search_results:
           id = search_result['id']
           content = search_result['content']
           score = search_result['@search.score']
           title = search_result['title']
           filepath = search_result['filepath']
           url = search_result['url']
           results.append({"id": id, "score": score, "content": content, "title": title, "filepath": filepath, "url": url})
           i += 1

        #print(type(results))
        return results

    def search_vector_query(self,request_msg):
        self.search_results = self.search_client.search(
            search_text=request_msg, # 全文検索も並行して評価する
            vector=self.openaiEmbd(request_msg), # ベクトルクエリ
            vector_fields='contentVector',
            top_k=5,
            top=5
        )
        results = []
        i = 0
        for search_result in self.search_results:
           id = search_result['id']
           content = search_result['content']
           score = search_result['@search.score']
           title = search_result['title']
           filepath = search_result['filepath']
           url = search_result['url']
           results.append({"id": id, "score": score, "content": content, "title": title, "filepath": filepath, "url": url})
           i += 1

        #print(type(results))
        return results

