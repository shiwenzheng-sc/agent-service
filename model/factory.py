from abc import abstractmethod,ABC
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from typing import Optional
from utils.config_handler import rag_conf

class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel ]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel ]:
        return ChatOpenAI(model=rag_conf["chat_model_name"],base_url=rag_conf["OPENAI_BASE_URL"])

class EmbeddingModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel ]:
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])

chat_model = ChatModelFactory().generator()
embed_model = EmbeddingModelFactory().generator()

