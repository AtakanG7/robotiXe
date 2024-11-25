import streamlit as st
from utils.auth_manager import GithubAuthManager
from utils.pdf_processor import PDFProcessor
from utils.database_manager import DatabaseManager
from utils.conversation_manager import ConversationManager
import os
from dotenv import load_dotenv

load_dotenv()

def load_chat_history(session_id, db_manager):
    """Load chat history and update session state"""
    chat_history = db_manager.get_session_history(session_id)
    if chat_history:
        st.session_state.messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in chat_history
        ]
        st.session_state.current_session_id = session_id
        return True
    return False

def show_auth_sidebar(auth_manager):
    with st.sidebar:
        st.title("Authentication")
        if not auth_manager.is_authenticated():
            st.write("Please login to continue")
            auth_manager.begin_auth()
        else:
            user_data = st.session_state['user']
            st.write(f"Welcome, {user_data['login']}")
            if st.button("Sign Out", key="signout_button"):
                auth_manager.logout()
                st.session_state.clear()
                st.experimental_rerun()

def show_chat_interface(authenticated, db_manager, user_data=None):
    st.title("PDF Chat Assistant")
    
    if not authenticated:
        st.info("Please authenticate via the sidebar to begin")
        with st.container():
            st.markdown("""
            <div style='background-color: #ffffff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <h3>Available Features</h3>
                <ul>
                    <li>PDF document analysis and processing</li>
                    <li>Natural language querying</li>
                    <li>AI-powered document insights</li>
                    <li>Conversation history management</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        return

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
        
    github_id = str(user_data['id'])
    
    # Display user stats
    user_stats = db_manager.get_user_stats(github_id)
    if user_stats:
        remaining_questions = 3 - user_stats[3]
        st.markdown(f"""
            <div style='background-color: #ffffff; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <p>Available questions today: {remaining_questions}/3</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Chat history selection in sidebar
    with st.sidebar:
        st.title("Chat History")
        sessions = db_manager.get_user_sessions(github_id)
        
        if sessions:
            session_options = {
                f"{s[1]} - {s[2][:10]} ({s[4]} msgs)": s[0] 
                for s in sessions
            }
            selected_session = st.selectbox(
                "Select conversation",
                options=["New Conversation"] + list(session_options.keys()),
                key="session_select",
                index=0  # Always default to "New Conversation"
            )
            
            if selected_session != "New Conversation":
                session_id = session_options[selected_session]
                if st.button("Load Selected Chat"):
                    if session_id != st.session_state.get('current_session_id'):
                        if load_chat_history(session_id, db_manager):
                            st.session_state.pdf_processed = True
                            st.experimental_rerun()
            
            if st.button("Start New Chat", key="new_chat_button"):
                st.session_state.clear()
                st.session_state.messages = []
                st.session_state.current_session_id = None
                st.session_state.pdf_processed = False
                st.experimental_rerun()
    
    # PDF upload interface
    if not st.session_state.get('pdf_processed', False):
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background-color: #ffffff; 
                border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <h3>Upload Document</h3>
                <p>Select or drag a PDF file to begin analysis</p>
            </div>
        """, unsafe_allow_html=True)
        
        pdf = st.file_uploader(
            "Select PDF",
            accept_multiple_files=False,
            type='pdf',
            key="pdf_upload"
        )
        
        if pdf:
            with st.spinner("Processing document..."):
                pdf_processor = PDFProcessor(pdf)
                pdf_text = pdf_processor.process()
                
                if pdf_text:
                    stats = pdf_processor.get_summary_stats()
                    with st.expander("Document Information"):
                        st.markdown(f"""
                            <div style='background-color: #ffffff; padding: 1rem; border-radius: 8px;'>
                                <p>Pages: {stats['total_pages']}</p>
                                <p>Word count: {stats['total_words']:,}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Create new session for uploaded PDF
                    session_id = db_manager.create_chat_session(github_id, pdf.name)
                    st.session_state.current_session_id = session_id
                    st.session_state.conversation_manager = ConversationManager(
                        pdf_text=pdf_text,
                        temperature=0.7,
                        api_key=os.getenv('OPENAI_API_KEY'),
                        session_id=session_id,
                        db_manager=db_manager
                    )
                    st.session_state.pdf_processed = True
                    st.experimental_rerun()

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if st.session_state.get('pdf_processed', False):
        if not db_manager.can_ask_question(github_id):
            st.error("Daily question limit reached. Please try again tomorrow.")
            return
            
        question = st.chat_input("Enter your question...")
        
        if question:
            # Increment question count and update messages
            db_manager.increment_question_count(github_id)
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Process the question and get response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                response = st.session_state.conversation_manager.ask_question(
                    question, 
                    message_placeholder
                )
                full_response = response["response"]
                message_placeholder.markdown(full_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
            
            # Force refresh to show new messages
            st.experimental_rerun()

def main():
    st.set_page_config(
        page_title="PDF Chat Assistant",
        page_icon=None,
        layout="wide"
    )
    
    db_manager = DatabaseManager()
    auth_manager = GithubAuthManager()
    auth_manager.complete_auth()
    
    show_auth_sidebar(auth_manager)
    show_chat_interface(
        authenticated=auth_manager.is_authenticated(),
        db_manager=db_manager,
        user_data=st.session_state.get('user', None)
    )

if __name__ == "__main__":
    main()