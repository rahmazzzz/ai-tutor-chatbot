# Chat Tutor – AI Voice & Chat Assistant

**Chat Tutor** is an AI-powered chatbot and voice assistant designed to enhance your learning experience. It uses a multi-agent orchestration system to intelligently decide how to help you based on your input. Whether you need web research, YouTube summaries, structured study plans, or semantic search within your documents, Chat Tutor has you covered.

---

## Features

### 1. Multi-Modal Interaction
- **Text Chat:** Ask questions or request learning resources directly via chat.
- **Voice Input/Output:** Speak with Chat Tutor and receive audio responses using STT/TTS integration.

### 2. Orchestrated LLM Intelligence
- A central LLM orchestrator decides which agent to trigger based on user input:
  - **Web Search Agent** – Search the web and provide curated results.
  - **YouTube Summarizer** – Summarize YouTube videos into concise notes.
  - **Study Planner Agent** – Generate a personalized study plan with:
    - Tasks divided by topics
    - Estimated time per task
    - Recommended sources and references
  - **Document Search & Summarization** – Upload PDFs, articles, or notes and query them semantically.

### 3. Content Summarization
- Summarizes videos, articles, and uploaded documents.
- Supports multi-step reasoning and provides concise explanations.

### 4. File Upload & Query
- Upload documents (PDF, TXT, DOCX) and ask questions directly from the content.
- Semantic search powered by embeddings and vector stores (e.g., Qdrant, pgVector).

### 5. Adaptive Learning & Study Management
- Generates personalized study plans.
- Breaks topics into tasks with time estimates.
- Suggests sources, videos, and articles for each task.

### 6. Multi-Agent Architecture
- Agents are modular and follow a best-practice, clean architecture design.
- Orchestrator manages communication between agents.
- Each agent handles a specific domain: web, YouTube, document, or study planning.
 
## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chat_tutor.git
cd chat_tutor
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configure environment variables in .env:

ini
Copy code
MONGO_URI=<your_mongo_connection_string>
JWT_SECRET=<your_secret_key>
OPENAI_API_KEY=<your_openai_api_key>
COHERE_API_KEY=<your_cohere_api_key>
Usage
Run the FastAPI server:

bash
Copy code
uvicorn app.main:app --reload
Access the interactive API docs:

arduino
Copy code
http://127.0.0.1:8000/docs
Use the Streamlit or web frontend to interact with:

Chat interface

Voice input/output

Document uploads

Study plan generation

Example Scenarios
Ask Chat Tutor:
"I want to learn Python for data analysis in 7 days."
→ Generates a task-by-task study plan with resources and estimated times.

Web Search:
"Find recent articles on GPT-5 applications"
→ Provides curated search results.

YouTube Summarization:
"Summarize the video: <YouTube link>"
→ Returns key points and a summary.

Document Query:
Upload ML_notes.pdf and ask: "Explain gradient descent"
→ Retrieves relevant sections and explains.

Technology Stack
Backend: FastAPI, Python

Database: MongoDB (user & session management)

Vector Search: Qdrant / pgVector

LLM: OpenAI GPT, Cohere

Voice: STT/TTS (optional: ElevenLabs)

Orchestration: Multi-agent LLM orchestrator for intelligent task delegation

Frontend: Streamlit / Custom web interface

Contributing
Contributions are welcome! Please follow best practices:

Use feature branches

Write clear commit messages

Follow the modular architecture

Ensure proper testing for new services or agents

License
MIT License © 2025 Rahma Hassan

