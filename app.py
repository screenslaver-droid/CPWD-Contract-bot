import streamlit as st
import os
import tempfile
from pathlib import Path
import time

# Try to import our modules with error handling
try:
    from ingest import ContractIngestor
    from qa_chain import CPWDContractQA, CPWD_SAMPLE_QUESTIONS
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required packages are installed. Run: pip install -r requirements.txt")
    st.stop()
except Exception as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="CPWD Contract Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c5f2d;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f4e79;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    .stButton > button {
        background-color: #1f4e79;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2c5f2d;
    }
</style>
""", unsafe_allow_html=True)

def update_env_file(api_key):
    """Update or create .env file with the API key"""
    env_file_path = Path(".env")
    
    try:
        # Read existing .env file if it exists
        if env_file_path.exists():
            with open(env_file_path, 'r') as f:
                lines = f.readlines()
            
            # Check if OPENAI_API_KEY already exists
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith("OPENAI_API_KEY="):
                    lines[i] = f"OPENAI_API_KEY={api_key}\n"
                    updated = True
                    break
            
            # If not found, add it
            if not updated:
                lines.append(f"OPENAI_API_KEY={api_key}\n")
        else:
            # Create new .env file
            lines = [f"OPENAI_API_KEY={api_key}\n"]
        
        # Write back to .env file
        with open(env_file_path, 'w') as f:
            f.writelines(lines)
        
        return True
        
    except Exception as e:
        st.error(f"Error updating .env file: {str(e)}")
        return False

def load_env_file():
    """Load environment variables from .env file"""
    env_file_path = Path(".env")
    
    if env_file_path.exists():
        try:
            with open(env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            return True
        except Exception as e:
            st.error(f"Error loading .env file: {str(e)}")
            return False
    return False

def initialize_session_state():
    """Initialize session state variables"""
    if 'qa_system' not in st.session_state:
        st.session_state.qa_system = CPWDContractQA()
    if 'ingestor' not in st.session_state:
        st.session_state.ingestor = ContractIngestor()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'contracts_loaded' not in st.session_state:
        st.session_state.contracts_loaded = False
    if 'env_loaded' not in st.session_state:
        st.session_state.env_loaded = load_env_file()

def upload_and_process_contracts():
    """Handle contract upload and processing"""
    st.markdown('<div class="sub-header">📁 Upload Contract Documents</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        accept_multiple_files=True,
        type=['pdf'],
        help="Upload one or more CPWD contract PDF files"
    )
    
    if uploaded_files:
        if st.button("Process Contracts", key="process_btn"):
            with st.spinner("Processing contracts..."):
                processed_count = 0
                failed_count = 0
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        # Update progress
                        progress = (i + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {uploaded_file.name}...")
                        
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Process the contract
                        success = st.session_state.ingestor.process_contract(
                            tmp_path, 
                            uploaded_file.name
                        )
                        
                        if success:
                            processed_count += 1
                        else:
                            failed_count += 1
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        failed_count += 1
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Show results
                if processed_count > 0:
                    st.success(f"Successfully processed {processed_count} contract(s)")
                    st.session_state.contracts_loaded = True
                    
                    # Force reload of QA system
                    st.session_state.qa_system = CPWDContractQA()
                    
                if failed_count > 0:
                    st.error(f"Failed to process {failed_count} contract(s)")
                
                # Rerun to update the contract info
                st.rerun()

def display_contract_info():
    """Display information about loaded contracts"""
    if st.session_state.contracts_loaded or st.session_state.ingestor.load_vector_store():
        info = st.session_state.ingestor.get_contract_info()
        
        if info["total_chunks"] > 0:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(f"**📊 Contract Database Status:**")
            st.markdown(f"- Total document chunks: {info['total_chunks']}")
            st.markdown(f"- Number of contracts: {len(info['contracts'])}")
            
            if info['contracts']:
                st.markdown("**📄 Loaded Contracts:**")
                for contract in info['contracts']:
                    st.markdown(f"  • {contract}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            return True
        else:
            st.warning("No contracts loaded yet. Please upload PDF files to get started.")
            return False
    else:
        st.info("Upload contract documents to begin analysis.")
        return False

def handle_question_answering():
    """Handle the Q&A interface"""
    st.markdown('<div class="sub-header">❓ Ask Questions About Your Contracts</div>', unsafe_allow_html=True)
    
    # Sample questions
    with st.expander("💡 Sample Questions", expanded=False):
        st.markdown("**Common CPWD Contract Questions:**")
        for i, question in enumerate(CPWD_SAMPLE_QUESTIONS[:10], 1):
            if st.button(f"{i}. {question}", key=f"sample_{i}"):
                st.session_state.current_question = question
                st.rerun()
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., What are the payment terms in the contract?",
        key="question_input"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        ask_button = st.button("Ask Question", key="ask_btn")
    
    with col2:
        if st.button("Clear Chat History", key="clear_btn"):
            st.session_state.chat_history = []
            st.session_state.qa_system.clear_memory()
            st.rerun()
    
    # Process question
    if ask_button and question:
        with st.spinner("Finding answer..."):
            result = st.session_state.qa_system.ask_question(question)
            
            if "error" not in result:
                # Add to chat history
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result["answer"],
                    "sources": result["sources"],
                    "timestamp": time.time()
                })
                
                # Clear the input
                st.session_state.current_question = ""
                st.rerun()
            else:
                st.error(result["error"])

def display_chat_history():
    """Display the chat history"""
    if st.session_state.chat_history:
        st.markdown('<div class="sub-header">💬 Conversation History</div>', unsafe_allow_html=True)
        
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 conversations
            with st.expander(f"Q: {chat['question'][:60]}...", expanded=(i == 0)):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                
                if chat['sources']:
                    st.markdown("**📚 Sources:**")
                    for j, source in enumerate(chat['sources'][:3]):  # Show top 3 sources
                        st.markdown('<div class="source-box">', unsafe_allow_html=True)
                        st.markdown(f"**Source {j+1}:** {source['metadata'].get('source_file', 'Unknown')}")
                        st.markdown(f"**Excerpt:** {source['content']}")
                        st.markdown('</div>', unsafe_allow_html=True)

'''def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🏗️ CPWD Contract Analyzer</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 Navigation")
        
        # API Key input
        current_api_key = os.environ.get("OPENAI_API_KEY", "")
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=current_api_key,
            help="Enter your OpenAI API key to use the Q&A feature"
        )
        
        if api_key and api_key != current_api_key:
            # Update environment variable
            os.environ["OPENAI_API_KEY"] = api_key
            
            # Update .env file
            if update_env_file(api_key):
                st.success("API Key set and saved to .env file successfully!")
            else:
                st.warning("API Key set in session but failed to save to .env file.")
        elif api_key:
            st.success("API Key is set!")
        
        st.markdown("---")
        
        # Contract management
        st.markdown("### 📄 Contract Management")
        
        # Show contract info
        contracts_available = display_contract_info()
        
        # Upload section
        st.markdown("### ⬆️ Upload New Contracts")
        if st.button("Upload Contracts", key="upload_toggle"):
            st.session_state.show_upload = not st.session_state.get('show_upload', False)
        
        # Instructions
        st.markdown("---")
        st.markdown("### 📖 Instructions")
        st.markdown("""
        1. **Upload**: Add your CPWD contract PDF files
        2. **Process**: Wait for documents to be processed
        3. **Ask**: Enter questions about your contracts
        4. **Analyze**: Review answers and source references
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        if st.button("Reset All Data", key="reset_btn"):
            # Clear vector store
            vector_store_path = "vector_store"
            if os.path.exists(vector_store_path):
                import shutil
                shutil.rmtree(vector_store_path)
            
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.success("All data cleared!")
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Upload section
        if st.session_state.get('show_upload', True):
            upload_and_process_contracts()
        
        # Q&A section
        if contracts_available and api_key:
            handle_question_answering()
        elif not api_key:
            st.info("Please enter your OpenAI API key in the sidebar to use the Q&A feature.")
        else:
            st.info("Please upload and process contracts first.")
    
    with col2:
        # Chat history
        display_chat_history()
        
        # Additional features
        if contracts_available:
            st.markdown("---")
            st.markdown('<div class="sub-header">🔍 Document Search</div>', unsafe_allow_html=True)
            
            search_query = st.text_input(
                "Search in contracts:",
                placeholder="Enter keywords to search..."
            )
            
            if search_query:
                with st.spinner("Searching..."):
                    docs = st.session_state.qa_system.get_relevant_documents(search_query)
                    
                    if docs:
                        st.markdown("**📄 Search Results:**")
                        for i, doc in enumerate(docs, 1):
                            with st.expander(f"Result {i} - {doc['source']}"):
                                st.markdown(doc['content'])
                    else:
                        st.info("No relevant documents found.")'''
def main():
    """Main application"""
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header"> CPWD Contract Analyzer</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 Navigation")

        # Contract management
        st.markdown("### 📄 Contract Management")
        contracts_available = display_contract_info()

        # Upload section
        st.markdown("### ⬆️ Upload New Contracts")
        if st.button("Upload Contracts", key="upload_toggle"):
            st.session_state.show_upload = not st.session_state.get('show_upload', False)

        # Instructions
        st.markdown("---")
        st.markdown("### 📖 Instructions")
        st.markdown("""
        1. **Upload**: Add your CPWD contract PDF files  
        2. **Process**: Wait for documents to be processed  
        3. **Ask**: Enter questions about your contracts  
        4. **Analyze**: Review answers and source references
        """)

        # Settings
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        if st.button("Reset All Data", key="reset_btn"):
            vector_store_path = "vector_store"
            if os.path.exists(vector_store_path):
                import shutil
                shutil.rmtree(vector_store_path)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("All data cleared!")
            st.rerun()

    # Main Content
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.session_state.get('show_upload', True):
            upload_and_process_contracts()

        if contracts_available:
            handle_question_answering()
        else:
            st.info("Please upload and process contracts to begin.")

    with col2:
        display_chat_history()

        if contracts_available:
            st.markdown("---")
            st.markdown('<div class="sub-header">🔍 Document Search</div>', unsafe_allow_html=True)
            search_query = st.text_input("Search in contracts:", placeholder="Enter keywords to search...")

            if search_query:
                with st.spinner("Searching..."):
                    docs = st.session_state.qa_system.get_relevant_documents(search_query)
                    if docs:
                        st.markdown("**📄 Search Results:**")
                        for i, doc in enumerate(docs, 1):
                            with st.expander(f"Result {i} - {doc['source']}"):
                                st.markdown(doc['content'])
                    else:
                        st.info("No relevant documents found.")

if __name__ == "__main__":
    main()