# 🩺 AI Symptom Checker (RAG Powered)

An intelligent AI-powered symptom checker that analyzes user input symptoms and provides structured medical insights including possible causes, home remedies, over-the-counter (OTC) medicines, and guidance on when to consult a doctor.

This project leverages a **Retrieval-Augmented Generation (RAG)** pipeline to ensure responses are grounded in a curated medical dataset rather than hallucinated by the model.

---

# 🚀 Features

* 🔍 Symptom-based analysis using natural language input
* 📚 Retrieval-Augmented Generation (RAG) for accurate responses
* 💊 Suggests safe OTC medications
* 🏠 Provides home remedies
* ⚠️ Advises when to consult a doctor
* 🧠 Uses structured medical dataset (JSON)
* 💡 Clean and simple UI using Streamlit
* 💸 Cost-efficient (uses free embeddings + Gemini API)

---

# 🏗️ Tech Stack

| Component       | Technology Used                  |
| --------------- | -------------------------------- |
| Frontend        | Streamlit                        |
| LLM             | Google Gemini (AI Studio API)    |
| Framework       | LangChain                        |
| Embeddings      | HuggingFace (`all-MiniLM-L6-v2`) |
| Vector Database | FAISS                            |
| Dataset         | Custom Medical JSON Dataset      |

---

# 🧠 How It Works

This project uses a **RAG (Retrieval-Augmented Generation)** pipeline:

1. **User Input**
   The user enters symptoms (e.g., "I have fever and headache").

2. **Embedding Generation**
   The input is converted into vector embeddings using HuggingFace models.

3. **Similarity Search (FAISS)**
   The system retrieves the most relevant medical conditions from the dataset.

4. **Context Injection**
   Retrieved data is passed as context to the LLM.

5. **LLM Response (Gemini)**
   The model generates a structured response:

   * Possible Causes
   * Home Remedies
   * OTC Medicines
   * When to See a Doctor

---

# 📂 Project Structure

```
AI_Symptom_Checker/
│
├── app.py                  # Streamlit UI
├── rag.py                  # RAG pipeline logic
├── ingest.py               # Converts dataset → vector DB
├── requirements.txt        # Dependencies
├── .gitignore              # Ignore sensitive/large files
│
├── data/
│   └── medical_knowledge.json   # Structured medical dataset
│
└── vector_db/              # Generated FAISS database (not pushed)
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```
git clone https://github.com/OM1307/AI_Symptom_Checker.git
cd AI_Symptom_Checker
```

---

## 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## 3️⃣ Add API Key

Create a `.env` file in root directory:

```
GOOGLE_API_KEY=your_api_key_here
```

---

## 4️⃣ Create Vector Database

```
python ingest.py
```

This step:

* Loads JSON dataset
* Converts to embeddings
* Stores in FAISS vector database

---

## 5️⃣ Run the Application

```
streamlit run app.py
```

---

# 📊 Dataset Design

The dataset is stored in structured JSON format:

* Condition Name
* Possible Causes
* Home Remedies
* OTC Medicines
* When to See a Doctor

This structured format improves:

* Retrieval accuracy
* Context relevance
* Response quality

---

# ⚠️ Disclaimer

This application is for **educational and informational purposes only**.

* It does **NOT provide medical diagnosis**
* It does **NOT replace professional medical advice**
* Always consult a qualified healthcare professional for serious conditions

---

# 🔥 Future Improvements

* 💬 Chat-based conversational interface
* 🧠 Memory (multi-turn conversations)
* 📈 Larger dataset (50+ diseases)
* 🌍 Deployment (Streamlit Cloud / AWS)
* 🧾 Symptom-to-disease mapping logic
* 🧠 Multi-modal input (voice/image)

---

# 🧠 Key Learnings

* Built a complete RAG pipeline using LangChain
* Implemented vector search with FAISS
* Integrated Gemini LLM for generation
* Designed structured dataset for better retrieval
* Handled real-world issues like API limits and model changes

---

# 👨‍💻 Author

**OM (AI Developer)**

* Focus: AI, RAG Systems, LLM Applications
* Passionate about building real-world AI products

---
