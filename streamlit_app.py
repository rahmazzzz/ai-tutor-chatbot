import streamlit as st
import asyncio
from sqlalchemy.orm import Session

from app.agents.voice_agent import VoiceAgent
from app.container.core_container import container
from app.services.notes_service import NotesService
from app.clients.supabase_client import get_db
from app.agents.chatbot_agent import ChatbotService
from app.services.voice_service import VoiceService
from app.graph.langgraph_chatbot import ChatbotGraph

# Initialize services from container
auth_service = container.auth_service
file_processing_service = container.file_processing_service
embedding_service = container.embedding_service
storage_service = container.storage_service
rag_service = container.rag_service
summarize_video_service = container.summarize_video_service

# Initialize additional services
notes_service = NotesService()

# ----------------- DB session for services -----------------
db: Session = next(get_db())
chat_service = ChatbotService(db=db)

# Initialize voice components
voice_service = VoiceService()
chatbot_graph = ChatbotGraph(db)
voice_agent_instance = VoiceAgent(db)

st.set_page_config(page_title="AI Tutor + Voice + Lecture Notes", layout="wide")

# --- Session state initialization ---
defaults = {
    "token": None,
    "messages": [],
    "last_transcript": None,
    "last_notes": None,
    "current_user": None
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.title("🔐 AI Tutor Auth & Chat")

# --- Tabs for Login/Register ---
tab1, tab2 = st.tabs(["Login", "Register"])

# ---------------- LOGIN ----------------
with tab1:
    st.subheader("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        try:
            auth_response = asyncio.run(auth_service.login(email=login_email, password=login_password))
            st.session_state.token = auth_response.access_token
            st.session_state.current_user = {
                "email": auth_response.user.email,
                "sub": auth_response.user.id
            }
            st.success(f"✅ Logged in successfully as {st.session_state.current_user['email']}")
        except Exception as e:
            st.error(f"❌ Login failed: {e}")

# ---------------- REGISTER ----------------
with tab2:
    st.subheader("Register")
    reg_email = st.text_input("Email", key="reg_email")
    reg_username = st.text_input("Username", key="reg_username")
    reg_password = st.text_input("Password", type="password", key="reg_password")

    if st.button("Register", key="register_btn"):
        try:
            user_out = asyncio.run(auth_service.register(
                email=reg_email,
                username=reg_username,
                password=reg_password
            ))
            st.session_state.current_user = {
                "email": user_out.email,
                "sub": user_out.id
            }
            st.success("✅ Registration successful! You can now log in.")
        except Exception as e:
            st.error(f"❌ Registration failed: {e}")

# ---------------- LOGGED IN TABS ----------------
if st.session_state.token and st.session_state.current_user:
    st.success(f"You are logged in as {st.session_state.current_user['email']} ✅")

    chat_tab, voice_tab, upload_tab, lecture_tab = st.tabs(
        ["💬 Chatbot", "🎙️ Voice Agent", "📄 Upload File", "📝 Lecture Notes"]
    )

    # ---------------- CHAT TAB ----------------
    with chat_tab:
        st.subheader("💬 Chat with AI Tutor")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display previous chat messages
        for role, msg in st.session_state.messages:
            st.chat_message(role).markdown(msg)

        # Input for new message
        if prompt := st.chat_input("Type your message...", key="chat_input"):
            st.session_state.messages.append(("user", prompt))
            st.chat_message("user").markdown(prompt)

            with st.spinner("AI Tutor is typing..."):
                try:
                    user_id = st.session_state.current_user["sub"]

                    async def get_chat_response():
                        # Use the chatbot graph (orchestrator) for general chat
                        result = await chatbot_graph.ainvoke({"message": prompt, "user_id": user_id})
                        response_text = result.get("response", "Sorry, I couldn't process that.")

                        # Normalize response type
                        if isinstance(response_text, list):
                            response_text = " ".join(str(r) for r in response_text)
                        elif isinstance(response_text, dict):
                            response_text = str(response_text)
                        return response_text

                    response_text = asyncio.run(get_chat_response())
                    st.session_state.messages.append(("assistant", response_text))
                    st.chat_message("assistant").markdown(response_text)

                except Exception as e:
                    try:
                        async def fallback_chat():
                            return await rag_service.chat(prompt, user_id)

                        fallback_response = asyncio.run(fallback_chat())
                        st.session_state.messages.append(("assistant", fallback_response))
                        st.chat_message("assistant").markdown(fallback_response)
                    except Exception as fallback_error:
                        fallback_msg = f"⚠️ I couldn't process that message. Error: {str(e)}"
                        st.session_state.messages.append(("assistant", fallback_msg))
                        st.chat_message("assistant").markdown(fallback_msg)

    # ---------------- VOICE TAB ----------------
    with voice_tab:
        st.subheader("🎙️ Voice Interaction")
        audio_upload = st.audio_input("🎤 Record your voice", key="voice_record")
        uploaded_file = st.file_uploader("Or upload a voice file", type=["wav", "mp3"], key="voice_file")

        if (audio_upload or uploaded_file) and st.button("Send Voice", key="voice_send"):
            if not st.session_state.current_user:
                st.warning("Please log in first!")
            else:
                with st.spinner("Processing voice..."):
                    try:
                        audio_bytes = None
                        file_name = None

                        if audio_upload is not None:
                            if isinstance(audio_upload, (bytes, bytearray, memoryview)):
                                audio_bytes = bytes(audio_upload)
                            elif hasattr(audio_upload, "read"):
                                audio_bytes = audio_upload.read()
                            file_name = "recorded_audio.wav"
                        elif uploaded_file is not None:
                            audio_bytes = uploaded_file.read()
                            file_name = getattr(uploaded_file, "name", "uploaded_audio")

                        if not isinstance(audio_bytes, (bytes, bytearray, memoryview)) or len(audio_bytes) == 0:
                            st.error("No valid audio input provided")
                            st.stop()

                        user_id = st.session_state.current_user["sub"]

                        async def process_voice():
                            return await voice_agent_instance.handle_audio(bytes(audio_bytes), user_id)

                        result = asyncio.run(process_voice())
                        transcript = result["text"]
                        st.session_state.last_transcript = transcript

                        st.subheader("📝 AI Response")
                        st.write(transcript)

                        st.subheader("🔊 AI Voice Reply")
                        st.audio(result["audio"], format="audio/wav")

                    except Exception as e:
                        st.error(f"Error: {e}")

    # ---------------- UPLOAD TAB ----------------
    with upload_tab:
        st.subheader("📄 Upload File for Embedding")
        file_to_upload = st.file_uploader("Select a file", type=["pdf", "txt", "docx"], key="upload_file")

        if file_to_upload and st.button("Upload File", key="upload_btn"):
            if not st.session_state.current_user:
                st.warning("Please log in first!")
            else:
                with st.spinner("Uploading and processing file..."):
                    try:
                        file_bytes = file_to_upload.read()
                        file_path = f"{st.session_state.current_user['sub']}/{file_to_upload.name}"

                        asyncio.run(storage_service.upload_file(
                            bucket="user-files",
                            file_path=file_path,
                            file_content=file_bytes,
                            token=st.session_state.token
                        ))

                        text = file_processing_service.extract_text_from_pdf(file_bytes)
                        chunks = file_processing_service.chunk_text(text)

                        asyncio.run(embedding_service.create_and_store_embeddings(
                            user_id=st.session_state.current_user["sub"],
                            filename=file_to_upload.name,
                            file_path=file_path,
                            chunks=chunks
                        ))

                        st.success("✅ File uploaded and embeddings stored")
                        st.info(f"Chunks created: {len(chunks)}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ---------------- LECTURE NOTES TAB ----------------
    with lecture_tab:
        st.subheader("📝 Live Lecture Notes")
        live_audio = st.audio_input("🎤 Record live lecture", key="lecture_audio")
        lecture_uploaded_file = st.file_uploader("Or upload lecture audio", type=["wav", "mp3"], key="lecture_file_upload")

        audio_to_process = None
        if live_audio is not None:
            if isinstance(live_audio, (bytes, bytearray, memoryview)):
                audio_to_process = bytes(live_audio)
            elif hasattr(live_audio, "read"):
                audio_to_process = live_audio.read()
        elif lecture_uploaded_file is not None:
            audio_to_process = lecture_uploaded_file.read()

        if audio_to_process and st.button("Generate Notes from Lecture", key="generate_lecture_notes"):
            if not st.session_state.current_user:
                st.warning("Please log in first!")
            else:
                with st.spinner("Transcribing and generating notes..."):
                    try:
                        if not isinstance(audio_to_process, (bytes, bytearray, memoryview)) or len(audio_to_process) == 0:
                            st.error("No valid audio provided for transcription")
                            st.stop()

                        async def generate_notes():
                            class MockFile:
                                def __init__(self, data):
                                    self._data = bytes(data)
                                async def read(self):
                                    return self._data
                            mock_file = MockFile(audio_to_process)
                            return await notes_service.generate_from_audio(mock_file)

                        transcript, notes = asyncio.run(generate_notes())
                        st.session_state.last_transcript = transcript
                        st.session_state.last_notes = notes

                        st.subheader("📝 Transcript")
                        st.text_area("Transcript", transcript, height=200)
                        st.subheader("📒 Generated Notes")
                        st.text_area("Notes", "\n".join(notes), height=200)
                    except Exception as e:
                        st.error(f"Error: {e}")
