import streamlit as st
from Utils.pdf_processor import PDFProcessor
from Utils.conversation_manager import ConversationManager
from Utils.question_generator import QuestionGenerator
from Utils.ui_components import sidebar_content, display_chat_messages

def main():
    st.header("Ask Questions To Your PDF 🗃️")

    pdf, api_key, temperature = sidebar_content()

    if pdf is not None:
        pdf_processor = PDFProcessor(pdf)
        
        if pdf_processor.is_new_pdf():
            vectorstore = pdf_processor.process()
            conversation_manager = ConversationManager(vectorstore, temperature, api_key)
            st.session_state["conversation_manager"] = conversation_manager

        question = st.text_input("Ask to Pdf", key="input")
        generate_questions = st.checkbox("GenerateQPDF")

        if generate_questions and question:
            st.info("You should choose one of them; cannot run at the same time!", icon="⚠️")
        elif question:
            conversation_manager = st.session_state["conversation_manager"]
            response = conversation_manager.ask_question(question)
            display_chat_messages(response["chat_history"])
        elif generate_questions:
            question_generator = QuestionGenerator(pdf_processor.get_text(), temperature, api_key)
            response = question_generator.generate()
            st.write(response)

if __name__ == "__main__":
    main()