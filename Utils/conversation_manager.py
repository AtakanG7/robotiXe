from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

class ConversationManager:
    def __init__(self, vectorstore, temperature, api_key):
        self.chain = self._create_conversation_chain(vectorstore, temperature, api_key)

    def _create_conversation_chain(self, vectorstore, temperature, api_key):
        llm = ChatOpenAI(temperature=temperature/10, model_name="gpt-3.5-turbo", openai_api_key=api_key)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        return ConversationalRetrievalChain.from_llm(
            llm=llm, retriever=vectorstore.as_retriever(), memory=memory)

    def ask_question(self, question):
        return self.chain({'question': question})