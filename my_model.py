import os
import dotenv

import sys
from pathlib import Path
from langchain_openai import AzureChatOpenAI as langchainAzureOpenAi

dotenv.load_dotenv()
openai_api_key = os.getenv("openai_api_key")
azure_endpoint = os.getenv("azure_endpoint")
api_version = os.getenv("api_version")


llm_langchain_4o = langchainAzureOpenAi(deployment_name='gpt-4o',
                      model_name='gpt-4o',
                      temperature=0.0,
                      openai_api_key=openai_api_key,
                      azure_endpoint=azure_endpoint,
                                 api_version=api_version)