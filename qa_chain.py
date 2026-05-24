import os
from typing import List, Dict, Any
from huggingface_hub import InferenceClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class CPWDContractQA:
    """
    A QA system for CPWD (Central Public Works Department) contracts using Mistral-7B via HuggingFace InferenceClient.
    """

    def __init__(self, vector_store_path: str = "vector_store"):
        self.vector_store_path = vector_store_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.llm = None
        self.vector_store = None
        self.setup_llm()

    def setup_llm(self) -> bool:
        try:
            hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if not hf_token:
                st.error("HuggingFace API token not found. Please set HUGGINGFACEHUB_API_TOKEN in environment.")
                return False

            self.llm = InferenceClient(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                token=hf_token
            )
            return True
        except Exception as e:
            st.error(f"Error setting up HuggingFace LLM: {str(e)}")
            return False

    def load_vector_store(self, filename: str = "contract_vectors") -> bool:
        try:
            vector_store_file = os.path.join(self.vector_store_path, filename)
            if os.path.exists(vector_store_file):
                self.vector_store = FAISS.load_local(
                    vector_store_file,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
            st.error(f"No vector store found at {vector_store_file}. Please upload and process contracts first.")
            return False
        except Exception as e:
            st.error(f"Error loading vector store: {str(e)}")
            return False

    def ask_question(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Ask a question using retrieved context and HuggingFace InferenceClient (chat format).

        Args:
            question: User query.
            k: Number of relevant chunks to retrieve.

        Returns:
            Dict with answer, sources, and original question.
        """
        if not self.llm:
            return {"error": "LLM client is not initialized."}

        if not self.vector_store:
            if not self.load_vector_store():
                return {"error": "Vector store not available"}

        try:
            # Retrieve relevant documents
            docs = self.vector_store.similarity_search(question, k=k)
            context = "\n\n".join(doc.page_content for doc in docs)

            # Prepare system and user messages
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert assistant for analyzing CPWD (Central Public Works Department) and related construction contracts. "
                        "Answer based strictly on the provided contract excerpts. "
                        "If the information is not available, say so clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:",
                },
            ]

            # Use chat completion
            response = self.llm.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=messages,
                max_tokens=512,
                temperature=0.3,
                top_p=0.9,
            )

            # Prepare sources
            sources = [{
                "content": doc.page_content[:300] + "...",
                "metadata": doc.metadata
            } for doc in docs]

            return {
                "answer": response.choices[0].message.content.strip(),
                "sources": sources,
                "question": question
            }

        except Exception as e:
            return {"error": f"Error processing question: {str(e)}"}


    def get_relevant_documents(self, query: str, k: int = 3) -> List[Dict]:
        if not self.vector_store:
            if not self.load_vector_store():
                return []
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [{
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source_file", "Unknown")
            } for doc in docs]
        except Exception as e:
            st.error(f"Error getting relevant documents: {str(e)}")
            return []

    def get_contract_summary(self) -> str:
        if not self.vector_store:
            if not self.load_vector_store():
                return "No contracts available"
        try:
            sample_docs = self.vector_store.similarity_search("contract terms conditions", k=3)
            contracts = {
                doc.metadata.get("contract_name") or doc.metadata.get("source_file")
                for doc in sample_docs
            }
            return f"Available contracts: {', '.join(filter(None, contracts))}" if contracts else "No named contracts found"
        except Exception as e:
            return f"Error getting contract summary: {str(e)}"

CPWD_SAMPLE_QUESTIONS = [
    "What are the key terms and conditions of this contract?",
    "What is the contract duration and completion timeline?",
    "What are the payment terms and schedule?",
    "What are the penalty clauses for delays?",
    "What are the material specifications mentioned?",
    "What are the quality standards and testing requirements?",
    "What are the safety requirements and protocols?",
    "What is the scope of work defined in the contract?",
    "What are the contractor's responsibilities?",
    "What are the dispute resolution mechanisms?"
]
