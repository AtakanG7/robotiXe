import os
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
import streamlit as st

class PDFProcessor:
    def __init__(self, pdf):
        self.pdf = pdf
        self.pdf_name = pdf.name.split(".")[0]
        self.text = ""

    def is_new_pdf(self):
        if self.pdf_name != st.session_state.get("pdf_name"):
            st.session_state["pdf_name"] = self.pdf_name
            self.text = self._read_pdf()
            return True
        return False

    def _read_pdf(self):
        text = ""
        reader = PdfReader(self.pdf)
        for page in reader.pages:
            text += page.extract_text()
        return text

    def process(self):
        pickle_path = f"{self.pdf_name}.pickle"
        if not os.path.exists(pickle_path):
            st.info('File is being embedded, please wait!', icon="ℹ️")
            vectorstore = self._create_vectorstore()
            with open(pickle_path, "wb") as file:
                pickle.dump(vectorstore, file)
        else:
            st.info('File is being loaded, please wait!', icon="ℹ️")
            with open(pickle_path, "rb") as file:
                vectorstore = pickle.load(file)
        return vectorstore

    def _create_vectorstore(self):
        chunks = self._create_text_chunks()
        embeddings = HuggingFaceInstructEmbeddings(
            model_name="sentence-transformers/distiluse-base-multilingual-cased-v2")
        return FAISS.from_texts(embedding=embeddings, texts=chunks)

    def _create_text_chunks(self, chunk_size=2000, chunk_overlap=300):
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        return splitter.split_text(self.text)

    def get_text(self):
        return self.text