import os
import pickle
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import streamlit as st

class ContractIngestor:
    def __init__(self, vector_store_path: str = "vector_store"):
        self.vector_store_path = vector_store_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF and return documents"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return documents
        except Exception as e:
            st.error(f"Error loading PDF: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents"""
        try:
            vector_store = FAISS.from_documents(documents, self.embeddings)
            return vector_store
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return None
    
    def save_vector_store(self, vector_store: FAISS, filename: str = "contract_vectors"):
        """Save vector store to disk"""
        try:
            os.makedirs(self.vector_store_path, exist_ok=True)
            vector_store.save_local(os.path.join(self.vector_store_path, filename))
            return True
        except Exception as e:
            st.error(f"Error saving vector store: {str(e)}")
            return False
    
    def load_vector_store(self, filename: str = "contract_vectors") -> FAISS:
        """Load vector store from disk"""
        try:
            vector_store_file = os.path.join(self.vector_store_path, filename)
            if os.path.exists(vector_store_file):
                vector_store = FAISS.load_local(
                    vector_store_file,
                    self.embeddings,
                    allow_dangerous_deserialization=True  # ✅ Fix: Enable controlled deserialization
                )
                return vector_store
            else:
                return None
        except Exception as e:
            st.error(f"Error loading vector store: {str(e)}")
            return None

    
    def add_documents_to_existing_store(self, documents: List[Document], filename: str = "contract_vectors"):
        """Add new documents to existing vector store"""
        try:
            existing_store = self.load_vector_store(filename)
            
            if existing_store is None:
                # Create new store if none exists
                new_store = self.create_vector_store(documents)
                if new_store:
                    self.save_vector_store(new_store, filename)
                    return new_store
            else:
                # Add to existing store
                existing_store.add_documents(documents)
                self.save_vector_store(existing_store, filename)
                return existing_store
        except Exception as e:
            st.error(f"Error adding documents to vector store: {str(e)}")
            return None
    
    def process_contract(self, file_path: str, contract_name: str = None) -> bool:
        """Process a single contract file"""
        try:
            # Load PDF
            documents = self.load_pdf(file_path)
            if not documents:
                return False
            
            # Add contract name as metadata
            if contract_name:
                for doc in documents:
                    doc.metadata['contract_name'] = contract_name
                    doc.metadata['source_file'] = os.path.basename(file_path)
            
            # Split documents
            chunks = self.split_documents(documents)
            
            # Add to vector store
            vector_store = self.add_documents_to_existing_store(chunks)
            
            return vector_store is not None
        except Exception as e:
            st.error(f"Error processing contract: {str(e)}")
            return False
    
    def get_contract_info(self, filename: str = "contract_vectors") -> dict:
        """Get information about stored contracts"""
        try:
            vector_store = self.load_vector_store(filename)
            if vector_store is None:
                return {"total_chunks": 0, "contracts": []}
            
            # Get all documents
            docs = vector_store.docstore._dict.values()
            
            contracts = set()
            total_chunks = len(docs)
            
            for doc in docs:
                if 'contract_name' in doc.metadata:
                    contracts.add(doc.metadata['contract_name'])
                elif 'source_file' in doc.metadata:
                    contracts.add(doc.metadata['source_file'])
            
            return {
                "total_chunks": total_chunks,
                "contracts": list(contracts)
            }
        except Exception as e:
            return {"total_chunks": 0, "contracts": [], "error": str(e)}

def main():
    """Test the ingestor"""
    ingestor = ContractIngestor()
    
    # Example usage
    contracts_folder = "contracts"
    if os.path.exists(contracts_folder):
        for filename in os.listdir(contracts_folder):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(contracts_folder, filename)
                print(f"Processing {filename}...")
                success = ingestor.process_contract(file_path, filename)
                if success:
                    print(f"Successfully processed {filename}")
                else:
                    print(f"Failed to process {filename}")
    
    # Print info about stored contracts
    info = ingestor.get_contract_info()
    print(f"\nTotal chunks: {info['total_chunks']}")
    print(f"Contracts: {info['contracts']}")

if __name__ == "__main__":
    main()