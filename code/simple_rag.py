from pydoc import resolve
import openai
from llama_index.llms.openai import OpenAI as llama_index_OpenAI
from llama_index.core import VectorStoreIndex, Document, get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.llms.vllm import Vllm
from llama_index.core import Prompt, PromptTemplate
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
import os
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
import torch
import transformers
import io
import sys
import json
from datetime import datetime, timedelta

os.environ["CUDA_VISIBLE_DEVICES"] = "2"

with open('WikiHow_setting.json', 'r') as f:
    settings = json.load(f)

question = "How To Make a Cape"
documents1 = []
query = ''
Settings.embed_model = HuggingFaceEmbedding(model_name='all-MiniLM-L6-v2')
for key, value in settings.items():
    if key == question:
        query = value['0'][1]
        continue
    for v_key, v_value in value.items():
        if v_value == 'None':
            continue
        documents1.append(Document(text=key + '\n' + v_value[1], metadata={'key': key + '_' + v_key}))

index = VectorStoreIndex.from_documents(documents1, settings=Settings, use_async=True)
retriever = index.as_retriever(retriever_mode='embedding', similarity_top_k=3)
response = retriever.retrieve(question + '\n' + query)
print([[r.metadata['key'], r.text] for r in response])


