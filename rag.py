# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# LLM (Gemini)
from langchain_google_genai import ChatGoogleGenerativeAI

# Embeddings (FREE)
from langchain_community.embeddings import HuggingFaceEmbeddings

# Vector DB
from langchain_community.vectorstores import FAISS


# -------------------------------
# 1. Initialize Embeddings (FREE)
# -------------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# -------------------------------
# 2. Load Vector Database
# -------------------------------
db = FAISS.load_local(
    "vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(search_kwargs={"k": 3})


# -------------------------------
# 3. Initialize Gemini LLM
# -------------------------------
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

llm = ChatGoogleGenerativeAI(
    model=gemini_model,
    temperature=0.5
)


# -------------------------------
# 4. Generate Response Function
# -------------------------------
def generate_response(user_input):
    try:
        # Retrieve relevant documents
        docs = retriever.invoke(user_input)

        # Combine context
        context = "\n".join([doc.page_content for doc in docs])

        # Prompt
        prompt = f"""
You are a safe and helpful medical assistant.

Use the provided context to answer accurately.
Do NOT hallucinate.

Context:
{context}

User symptoms:
{user_input}

Provide output in this format:

1. Possible Causes:
- ...

2. Home Remedies:
- ...

3. OTC Medicines:
- ...

4. When to See a Doctor:
- ...

⚠️ Disclaimer:
This is not medical advice. Consult a doctor for serious conditions.
"""

        # Get response from Gemini
        response = llm.invoke(prompt)

        return response.content

    except Exception as e:
        return f"Error: {str(e)}"
