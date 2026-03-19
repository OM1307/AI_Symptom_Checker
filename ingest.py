# -----------------------------------
# Load environment variables (optional)
# -----------------------------------
from dotenv import load_dotenv
import os

load_dotenv()


# -----------------------------------
# Imports
# -----------------------------------
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# -----------------------------------
# 1. Load JSON file
# -----------------------------------
with open("data/medical_knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# -----------------------------------
# 2. Convert JSON → LangChain Documents
# -----------------------------------
documents = []

for condition in data["conditions"]:
    text = f"""
Condition: {condition['name']}

Possible Causes:
{', '.join(condition['possible_causes'])}

Home Remedies:
{', '.join(condition['home_remedies'])}

OTC Medicines:
{', '.join(condition['otc_medicines'])}

When to See a Doctor:
{', '.join(condition['when_to_see_doctor'])}
"""

    documents.append(Document(page_content=text))


# -----------------------------------
# 3. Split into chunks
# -----------------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

docs = text_splitter.split_documents(documents)


# -----------------------------------
# 4. Create Embeddings (FREE)
# -----------------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# -----------------------------------
# 5. Store in FAISS Vector DB
# -----------------------------------
db = FAISS.from_documents(docs, embeddings)

db.save_local("vector_db")


# -----------------------------------
# Done
# -----------------------------------
print("Vector DB created successfully!")