from utils.config_handler import chroma_conf
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from model.factory import embed_model
from utils.file_handler import get_file_md5_hex,pdf_loader,txt_loader,listdir_with_allowed_type
from utils.path_tool import get_abs_path
from utils.logger_handler import logger
from langchain_core.documents import Document
import os

class VectorStoreService():
    def __init__(self):
        #创建chroma实例对象
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"]
        )
        #创建递归文本分割器实例对象
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = chroma_conf["chunk_size"],
            chunk_overlap = chroma_conf["chunk_overlap"],
            separators = chroma_conf["separators"],
            length_function = len
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k":chroma_conf["k"]})

    def load_document(self):
        #加载文档内容
        md5_path = get_abs_path(chroma_conf["md5_hex_store"])
        def check_md5(md5_hex:str):
            #检查文件是否已经存过
            if not os.path.exists(md5_path):
                logger.info("md5存储文件不存在已创建")
                open (md5_path,"w").close()
                return False
            with open (md5_path,"r",encoding="utf-8") as f:
                for line in f.readlines():
                    if md5_hex == line.strip():
                        return True
                return False

        def save_md5(md5_hex:str):
            #保存文档md5值
            with open(md5_path,"a",encoding="utf-8")  as f:
                f.write(md5_hex+"\n")

        def get_file_documents(file_path) -> list[Document]:
            if file_path.endswith("txt"):
                return txt_loader(file_path)
            if file_path.endswith("pdf"):
                return pdf_loader(file_path)
            return []
        allow_file_path = listdir_with_allowed_type(get_abs_path(chroma_conf["data_path"]),allowed_end=tuple(chroma_conf["allow_knowledge_file_type"]))
        for file in allow_file_path:
            md5 = get_file_md5_hex(file)
            if check_md5(md5):
                logger.info(f"[加载知识库]{file}已入库，跳过")
                continue
            try:  
                docs = get_file_documents(file)
                if not docs:
                    logger.warning(f"[加载知识库]{file}无有效文本，跳过")
                    continue
                data = self.splitter.split_documents(docs)
                if not data:
                    logger.warning(f"[加载知识库]{file}分片后无内容，跳过")
                    continue
                self.vector_store.add_documents(data)
                save_md5(md5)
                logger.info(f"[加载知识库]{file}成功")
            except Exception as e:                    # ⑧ 和 try 同级
                logger.error(f"[加载知识库]{file}加载失败：{str(e)}", exc_info=True)
                continue
if __name__ == "__main__":
    vs = VectorStoreService()
    vs.load_document()

    retriever = vs.get_retriever()
    for doc in retriever.invoke("故障"):
        print(doc.page_content[:60])
        print("-" * 20)