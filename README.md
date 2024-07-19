# PDF Question-Answer & Question Generation with Langchain
This project provides a powerful chatbot that allows users to interact with their PDF documents by asking questions and receiving accurate answers. Additionally, it can generate relevant questions from the content of the PDFs. This chatbot can be easily integrated into Python-based frameworks like Flask.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://smartpdf.onrender.com/)

https://github.com/user-attachments/assets/5f4c47cd-9ee3-4670-8b47-dc46607524c3


## 🌟 Key Features

- **Interactive Q&A**: Chat with your documents
- **Automatic Question Generation**: Create quizzes.
- **Smart Context Retrieval**: Get accurate answers
- **Easy Integration**: Python frameworks like Flask

## 🛠️ Under the Hood

### Question Generation

1. **Prompt Engineering**: Prompt to guide the AI.
2. **LLM Integration**: Leverage OpenAI's GPT models.
3. **Context Chunking**: Efficiently process.

### Document Chat

1. **Embeddings**: Vector representations
2. **Semantic Search**: Relevant context
3. **Conversational Memory**: Chat session
4. **Focused Responses**: Strictly based on document content
  
---
Let's start talking about what we expect from these conversation bots. We don't want them to give non-sense, unrelated answers. To avoid that we can either use prompts or conversation chains. In this case, we will be using chains. 

# Commitment To The Document
- **I gave this text which was in the document.**
![d](https://github.com/AtakanG7/langchain-qa/assets/115896304/e28b83e2-977d-4dda-a381-aa3ad67ac72f)
![c](https://github.com/AtakanG7/langchain-qa/assets/115896304/ac0214bd-ca98-40c6-bb75-e452fe140bff)
- **This doesnt entirely proves that only answers from the document so I had to be sure and I asked one more question.**
![b](https://github.com/AtakanG7/langchain-qa/assets/115896304/d4a0148a-579a-4f96-9617-309c4d653d31)
![a](https://github.com/AtakanG7/langchain-qa/assets/115896304/cae436b9-babe-46a5-9e96-5c92ea9f1399)
- **Overall, I'm convinced that this set-up only answers from the document.**
- **Whenever I ask non-sense question. It says ***"I don't know"*** which is what we expect.**
![Screenshot 2023-07-21 064108](https://github.com/AtakanG7/langchain-qa/assets/115896304/cff8353f-254f-4f97-bfdf-e02755b9bfc4)
![Screenshot 2023-07-21 064125](https://github.com/AtakanG7/langchain-qa/assets/115896304/8cdbe5b2-f4e2-4949-a0b0-da4d8a2480ed)

# How To Run On Local Systems
```python
    git clone https://github.com/AtakanG7/robotiXe.git
```

Create virtual envirement (required!) Trust me :)
```python
    python -m venv your_env_name
```
Now, the envirement is supposed to be added to your directory. You need to activate it. 

```python
    .your_env_name\Scripts\activate
```
Congratulations, you are half way there. Now install the dependencies.

```python
    pip install -r requirements.txt
```
This will take some time.
After all things set up, you need to run the project

```python
    streamlit run main.py
```

### Dependencies
* langchain
* openai
* PyPDF2 
* streamlit  
* InstructorEmbedding 
* sentence_transformers 
* faiss-cpu
* 
# Conclution

* If you have any questions you can e-mail me pwxcv7352@gmail.com 😊👋
* Good Luck!
