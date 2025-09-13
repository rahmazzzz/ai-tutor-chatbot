# 📚 AI Tutor with Voice & Memory  

An **AI-powered tutor platform** that combines **Supabase, LangChain, and LangGraph** to deliver personalized, multilingual, voice-enabled tutoring.  

## 🚀 Features  

- 🔐 **Multi-user authentication** via Supabase Auth  
- 📂 **File uploads** (PDFs, notes, audio) stored in Supabase Storage  
- 🧠 **Semantic search** using pgvector embeddings in Postgres  
- 🗣️ **Voice support** with Speech-to-Text (STT) & Text-to-Speech (TTS)  
- 🤖 **AI tutoring** powered by LangChain (explanations, quizzes, feedback)  
- 🔄 **Adaptive learning pipeline** orchestrated with LangGraph  
- 📊 **Realtime progress tracking** & analytics dashboards via Supabase subscriptions  
- 🌍 **Multilingual support** (English + Arabic, extendable)  
- 🎮 *Optional:* Gamification (badges, leaderboards), study groups, multi-agent tutor  

---

## 🛠 Tech Stack  

- **Backend:** FastAPI + LangChain + LangGraph  
- **Database:** Supabase Postgres + pgvector  
- **Auth & Storage:** Supabase (users, sessions, file uploads)  
- **LLMs:** OpenAI / HuggingFace / Cohere (configurable)  
- **Embeddings:** Sentence Transformers (HuggingFace)  
- **Voice:** OpenAI Whisper (STT) + ElevenLabs / gTTS (TTS)  
- **Deployment:** Docker + (Render / Fly.io / Vercel API / Supabase edge functions)  

---

## 🏗 Architecture  

```mermaid
flowchart TD
    subgraph User
        U1[Student] -->|Voice/Text| API
        U2[Teacher] -->|Analytics| API
    end

    subgraph Backend[FastAPI Backend]
        A1[Auth Routes] --> Supabase
        A2[Upload & Search Routes] --> Storage
        A3[Tutor Routes] --> LangGraph
    end

    subgraph Supabase
        DB[(Postgres + pgvector)]
        Storage[(Storage)]
        Auth[(Auth)]
        Realtime[(Subscriptions)]
    end

    subgraph AI
        LLM[LangChain + OpenAI/HF]
        Voice[STT + TTS]
    end

    API --> A1 & A2 & A3
    A2 --> Storage
    A3 --> DB
    A3 --> LLM
    A3 --> Voice
    Supabase --> Analytics
