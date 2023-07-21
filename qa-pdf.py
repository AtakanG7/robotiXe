from langchain.embeddings import HuggingFaceInstructEmbeddings
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate
import os
import pickle
from streamlit import chat_message
import random
from dotenv import load_dotenv

load_dotenv()

if not "pdfname" in st.session_state:
    st.session_state.pdfname = None

if not "text" in st.session_state:
    st.session_state.text = ""

if not "vectorStore" in st.session_state:
    st.session_state.vectorStore = None

if not "chain" in st.session_state:
    st.session_state.chain = None

if not "chain1" in st.session_state:
    st.session_state.chain1 = None

if not "key" in st.session_state:
    st.session_state.key = None

PROMPT = PromptTemplate.from_template(template=""" 
    given context generate 5 questions out of given context never give your opinion. If the information is not enough to 
    generate 5 questions, you must say "please provide more information". You must add options like a, b, c and d as possible answers to each generated questions.
                        
    context = {context}
                        
- Generate these questions in Turkish:
""")

def displayMessages(chat_history):
    count = 1
    for message in reversed(chat_history):
        if count % 2 == 0:
            with chat_message("user"):
                st.write(message.content)
        else:
            with chat_message("assistant"):
                st.write(message.content)
        count += 1

def readMyPdf(pdf):

    readPDF = PdfReader(pdf)
    for page in readPDF.pages:
        st.session_state.text += page.extract_text()
    

def extractMyEmbeddings():

    text_splitter = CharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=300,
        length_function=len
    )

    chunks = text_splitter.split_text(text=st.session_state.text)

    embeddings = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-xl")
    
    return FAISS.from_texts(embedding=embeddings, texts=chunks)


def setConversation(temperature):

    llm = OpenAI(temperature=temperature/10,
                 model_name="gpt-3.5-turbo", openai_api_key=st.session_state.key)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)
    
    st.session_state.chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=st.session_state.vectorStore.as_retriever(), memory=memory)

def setConversation_1(temperature):

    llm = OpenAI(temperature=temperature/10,
                 model_name="gpt-3.5-turbo", openai_api_key=st.session_state.key)
    st.session_state.chain1 = LLMChain(llm=llm, prompt=PROMPT)

def retrieve5Chunks():

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=2000,
        chunk_overlap=300,
        length_function=len
    )
    chunks = text_splitter.split_text(text=st.session_state.text)
    docs = text_splitter.create_documents(chunks)
    # Ensure that the number of chunks is at least 5 before sampling
    num_docs_to_select = min(5, len(docs))
    random_docs = random.sample(docs, num_docs_to_select)
    return random_docs

def main():

    st.header("Ask Questions To Your PDF 🗃️")
    
    with st.sidebar:

        st.image("./image/summarify-logo-300.png")
        "contacts"

        st.text("http:/summarify.io")

        pdf = st.file_uploader(
            label="Upload your pdf file below ", accept_multiple_files=False)
        
        st.session_state.key = st.text_input("Your Api Key ")

        temperature = st.slider(
            "Select:",
            0, 10, 1)

    if pdf is not None:

        pdfName = pdf.name.split(".")[0] # pdf name

        if not pdfName == st.session_state["pdfname"]: # checking current pdf or not

            st.session_state.text = ""
            readMyPdf(pdf)  # extract texts
            st.session_state["pdfname"] = pdfName

            # save or retrieve if exist
            if os.path.exists(f"{pdfName}.pickle"):
                st.info('file is being loaded, please wait! ', icon="ℹ️")

                with open(f"{pdfName}.pickle", "rb") as file:
                    st.session_state.vectorStore = pickle.load(file=file)
            else:
                st.info('file is being embedded, please wait! ', icon="ℹ️")

                st.session_state.vectorStore = extractMyEmbeddings()
                with open(f"{pdfName}.pickle", "wb") as file:
                    pickle.dump(st.session_state.vectorStore, file=file)

            # load the conversation
            setConversation(temperature)

        question = st.text_input("Ask to Pdf", key="input") # user question
        check = st.checkbox("GenerateQPDF") # check box
        
        if check and question:

            st.info("You should choose one of the them cannot run at the same time!", icon="⚠️")
            
        elif question:

            st.write("---")

            response = st.session_state.chain({'question': question})

            chat_history = response["chat_history"]
            displayMessages(chat_history)

            st.write("---")



        if check: # generates 5 questions and 4 options to them

            docs = retrieve5Chunks()
            setConversation_1(temperature=temperature)

            if question:
               
               st.info("Delete message box input before attempting this!", icon="📢")

            else:
                st.write("---")

                response = st.session_state.chain1(docs)
                st.write(response)

                st.write("---")

if __name__ == "__main__":
    main()
