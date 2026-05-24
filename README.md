<<<<<<< HEAD
# CPWD Contract Analyzer

A comprehensive Streamlit application for analyzing CPWD (Central Public Works Department) contracts using Large Language Models. This system allows users to upload contract PDFs, process them using vector embeddings, and ask questions about contract terms, conditions, and specifications.

## Features

- **PDF Upload & Processing**: Upload multiple CPWD contract PDFs simultaneously
- **Intelligent Document Processing**: Automatic text extraction and chunking for optimal retrieval
- **Vector Search**: FAISS-based similarity search for relevant document sections
- **Natural Language Q&A**: Ask questions about contracts in natural language
- **Source Attribution**: Get answers with references to specific document sections
- **Conversation History**: Track your questions and answers in a chat-like interface
- **Predefined Questions**: Common CPWD contract questions for quick analysis
- **Document Search**: Search for specific keywords across all uploaded contracts

## Project Structure

```
cpwd_contract_qa/
│
├── app.py                 # Main Streamlit application
├── ingest.py             # Document ingestion and vector store management
├── qa_chain.py           # Question-answering chain and LLM integration
├── contracts/            # Folder for contract PDFs (auto-created)
├── vector_store/         # FAISS index storage (auto-created)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd cpwd_contract_qa
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
```

5. **Configure your OpenAI API key**:
   - Edit `.env` file and add your OpenAI API key
   - Or enter it directly in the Streamlit sidebar

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Step-by-Step Guide

1. **Enter API Key**: 
   - Input your OpenAI API key in the sidebar
   - This is required for the Q&A functionality

2. **Upload Contracts**:
   - Click "Upload Contracts" in the sidebar
   - Select one or more PDF files containing CPWD contracts
   - Click "Process Contracts" to analyze the documents

3. **Ask Questions**:
   - Use the predefined sample questions or enter your own
   - Questions can be about:
     - Contract terms and conditions
     - Payment schedules
     - Technical specifications
     - Penalty clauses
     - Material requirements
     - Safety protocols
     - And more...

4. **Review Answers**:
   - Get detailed answers with source references
   - View conversation history
   - Search for specific keywords

### Sample Questions

The application includes predefined questions for common CPWD contract analysis:

- What are the key terms and conditions of this contract?
- What is the contract duration and completion timeline?
- What are the payment terms and schedule?
- What are the penalty clauses for delays?
- What are the material specifications mentioned?
- What are the quality standards and testing requirements?
- What are the safety requirements and protocols?
- What is the scope of work defined in the contract?

## Technical Components

### Document Processing (`ingest.py`)

- **PDF Loading**: Uses PyPDF2 for text extraction
- **Text Chunking**: RecursiveCharacterTextSplitter for optimal chunk sizes
- **Vector Embeddings**: HuggingFace sentence-transformers for semantic search
- **Vector Storage**: FAISS for efficient similarity search

### Question Answering (`qa_chain.py`)

- **Language Model**: OpenAI GPT-3.5-turbo for natural language understanding
- **Retrieval Chain**: LangChain ConversationalRetrievalChain for context-aware answers
- **Memory Management**: Conversation buffer for maintaining context
- **Custom Prompts**: Specialized prompts for CPWD contract analysis

### User Interface (`app.py`)

- **Streamlit Framework**: Interactive web interface
- **File Upload**: Multiple PDF upload with progress tracking
- **Chat Interface**: Conversation-style Q&A
- **Source Display**: Referenced document sections
- **Search Functionality**: Keyword search across documents

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0
VECTOR_STORE_PATH=vector_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Customization Options

- **Chunk Size**: Adjust document chunk size for processing
- **Overlap**: Control overlap between chunks for better context
- **Model Selection**: Choose different OpenAI models
- **Temperature**: Control response creativity (0 = deterministic)
- **Retrieval Parameters**: Adjust number of relevant documents retrieved

## Dependencies

- **streamlit**: Web application framework
- **langchain**: LLM integration and chains
- **langchain-openai**: OpenAI integration
- **faiss-cpu**: Vector similarity search
- **PyPDF2**: PDF text extraction
- **sentence-transformers**: Text embeddings
- **python-dotenv**: Environment variable management
- **tiktoken**: Token counting for OpenAI models

## API Requirements

This application requires an OpenAI API key for the language model functionality. You can obtain one from:
- [OpenAI API Platform](https://platform.openai.com/)

## Limitations

- PDF files must be text-based (scanned images won't work without OCR)
- Large documents may take time to process
- API costs apply based on OpenAI usage
- Vector store is stored locally (not persistent across deployments)

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure your OpenAI API key is valid and has sufficient credits
   - Check that the key is properly set in the sidebar or .env file

2. **PDF Processing Errors**:
   - Ensure PDFs are not password-protected
   - Check that PDFs contain extractable text

3. **Memory Issues**:
   - Large documents may require more system memory
   - Consider reducing chunk size or processing fewer documents

4. **Slow Performance**:
   - First-time processing is slower due to model downloads
   - Subsequent queries are faster due to cached embeddings

### Debug Mode

To run in debug mode:

```bash
streamlit run app.py --logger.level=debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the code documentation
- Open an issue in the repository

## Acknowledgments

- Built with LangChain for LLM integration
- Uses OpenAI's GPT models for natural language processing
- FAISS for efficient vector similarity search
- Streamlit for the web interface
=======
# CPWD-Contract-bot
A comprehensive Streamlit application for analyzing CPWD (Central Public Works Department) contracts using Large Language Models. This system allows users to upload contract PDFs, process them using vector embeddings, and ask questions about contract terms, conditions, and specifications.
>>>>>>> af2285199c76c26c842dcaff5f11228335ae12e8
