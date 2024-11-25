from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage
import streamlit as st

class ConversationManager:
    def __init__(self, pdf_text, temperature, api_key, session_id, db_manager):
        self.pdf_text = pdf_text
        self.session_id = session_id
        self.db_manager = db_manager
        self.chat_history = []
        
        self.llm = ChatOpenAI(
            temperature=temperature/10, 
            model_name="gpt-3.5-turbo", 
            openai_api_key=api_key,
            streaming=True  # Enable streaming
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that answers questions about PDF documents.
            Base your answers ONLY on the provided PDF content below. If the answer cannot be found
            in the PDF content, clearly state that. Be concise and accurate.
            
            PDF Content:
            {pdf_content}
            
            Previous conversation:
            {chat_history}
            """),
            ("human", "{question}")
        ])

    def ask_question(self, question, message_placeholder):
        """Process a question and update chat history with streaming response"""
        chat_history_str = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in self.chat_history
        ])
        
        messages = self.prompt.format_messages(
            pdf_content=self.pdf_text,
            chat_history=chat_history_str,
            question=question
        )

        # Initialize empty response
        full_response = ""
        
        # Stream the response
        for chunk in self.llm.stream(messages):
            content = chunk.content
            full_response += content
            # Update placeholder with accumulated response
            message_placeholder.markdown(full_response + "▌")
        
        # Update placeholder one final time without cursor
        message_placeholder.markdown(full_response)
        
        # Update chat history
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=full_response))
        
        # Update chat history in database
        serialized_history = [
            {"role": "user" if isinstance(msg, HumanMessage) else "assistant", 
             "content": msg.content}
            for msg in self.chat_history
        ]
        self.db_manager.update_chat_history(self.session_id, serialized_history)
        
        return {
            "chat_history": self.chat_history,
            "response": full_response
        }