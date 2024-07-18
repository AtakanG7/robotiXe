# PDF Question-Answer & Question Generating (Langchain)
- Chat with your documents 📃
---
https://smartpdf.onrender.com/
---
## Question Generation
---
* In this section we'll start to talk more about code. Since generating questions extremly easy one, I wil discuss How we chat later on. 
* To generate question you only need to know how to write some **prompts** and have an **api key**.
```
PROMPT = PromptTemplate.from_template(template=""" 
    given context generate 5 questions out of given context never give your opinion. If the information is not enough to generate 5 questions,
     you must say "please provide more information". You must add options like a, b, c and d as possible answers to each generated questions.
                        
    context = {context}
                        
- Generate these questions in Turkish:
""")
```
* if you done creating your own prompt, lets continue creating our chain.
```
def setConversation_1(temperature):

    llm = OpenAI(temperature=temperature/10,
                 model_name="gpt-3.5-turbo", openai_api_key=st.session_state.key)

    st.session_state.chain1 = LLMChain(llm=llm, prompt=PROMPT)
```
* First, we need to understand some words here,
* ***temperature:*** means how deterministic the model should be. (0 to 1)
* ***model_name:*** in this case "gpt-3.5-turbo" which is the model used.
* After, knowing a little more, we can pass to helper functions.
* ***Reads uploaded documents***
```
def readMyPdf(pdf):

    readPDF = PdfReader(pdf)
    for page in readPDF.pages:
        st.session_state.text += page.extract_text()
```
* ***Chunk splitter function***
* There is a reason why that I use this function. Since we don't need a specific part of the given document, we only need to
* get at least 5 chunks thus we will extract our questions without needing to embeddings which is awasome.
```
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
```  
*   Finally, lets bring all these functions together
```
    docs = retrieve5Chunks()
    setConversation_1(temperature=temperature)

    response = st.session_state.chain1(docs)
    st.write(response)
```
end of the ***generating questions section***
---
## Chatting With Documents
---
* Since we need embeddings. Things will somehow mix up. Therefore, we better talk about ***dependencies**
### Dependencies
* langchain
* openai
* PyPDF2 
* streamlit  
* InstructorEmbedding 
* sentence_transformers 
* faiss-cpu
--- 
* Let's start talking about what we expect from these conversation bots. We don't want them to give non-sense, unrelated answers. To avoid that we can either use prompts or conversation chains. In this case, we will be using chains. 
---
## Commitment To The Document
---
- **I gave this text which was in the document.**
 ![d](https://github.com/AtakanG7/langchain-qa/assets/115896304/e28b83e2-977d-4dda-a381-aa3ad67ac72f)
 ![c](https://github.com/AtakanG7/langchain-qa/assets/115896304/ac0214bd-ca98-40c6-bb75-e452fe140bff)
- **it gave me this! This doesnt entirely proves that only answers from the document so I had to be sure and I asked one more question.**
![b](https://github.com/AtakanG7/langchain-qa/assets/115896304/d4a0148a-579a-4f96-9617-309c4d653d31)
![a](https://github.com/AtakanG7/langchain-qa/assets/115896304/cae436b9-babe-46a5-9e96-5c92ea9f1399)
- **Overall, I'm convinced that this set-up only answers from the document.**
- **Whenever I ask non-sense question. It says ***"I don't know"*** which is what we expect.**
![Screenshot 2023-07-21 064108](https://github.com/AtakanG7/langchain-qa/assets/115896304/cff8353f-254f-4f97-bfdf-e02755b9bfc4)
![Screenshot 2023-07-21 064125](https://github.com/AtakanG7/langchain-qa/assets/115896304/8cdbe5b2-f4e2-4949-a0b0-da4d8a2480ed)
---
* I'll be explaining things by showing the code.
```
def setConversation(temperature):

    llm = OpenAI(temperature=temperature/10,
                 model_name="gpt-3.5-turbo", openai_api_key=st.session_state.key)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)
    
    st.session_state.chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=st.session_state.vectorStore.as_retriever(), memory=memory)
```
* As seen llm is still required. We will use it to build our chain. Nothing changed, give the required arguments to the llm.
#### Differently There is Memory 
* Memory is a must, if you want to build a chat bot.
* There are a lot of memory out there. And each memory has its own feature.
* Check out more information https://python.langchain.com/docs/modules/memory/how_to/buffer_window
#### ***Embeddings***
* The most known embeddings today are HuggingFaceInstructEmbeddings and OpenAIEmbeddings
* There are pros and cons for each of these.
* Huggingface needs cpu usage to embed documents whereas openai needs your money 😊.
* Huggingface need a lot ⌛ to embed your file compared to openai.
* You need to be deciding according to your budget and use case.
* Since we are talking about embeddings lets see it in action.
* This is the function that we need to embed our documents (Huggingface used!)
```
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
```
* As always, lets bring the pieces together.
```
    chain = setConversation(temperature)
    response = chain({'question': question})

    chat_history = response["chat_history"]
    displayMessages(chat_history)
```
* displayMessages() is a work flow function which means has no good to the topic.
---
### How To Run On Local Systems
---
* I'm assuming you are using windows os.
* First of all clone my work.
```
    git clone https://github.com/AtakanG7/langchain-qa.git
```
* Make sure you're cloning it to a proper place you can find. You can make sure
* this by writing ***"pwd"*** to command line it will give you the exact path to your location
* After you make sure you're okay we need to download the dependencies. But I encourage you to
* create a virtual envirement to avoid any package conflicts. Here is how : 
```
    python -m venv your_env_name
```
" Now, the envirement is supposed to be added to your directory. You need to activate it. 
```
    .your_env_name\Scripts\activate
```
* Congratulations, you are half way there. Now install the dependencies.
```
    pip install -r requirements.txt
```
* This will take some time.
* After all things set up, you need to run the project
```
    streamlit run qa.pdf.py
```
---

* All in all, I tried my best to explain. Thanks for visiting.
* If you have any questions you can e-mail me pwxcv7352@gmail.com 😊👋
* Good Luck!
