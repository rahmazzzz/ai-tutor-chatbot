import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:8000"  # FastAPI backend

st.set_page_config(page_title="AI Chatbot + Voice", layout="wide")

# --- Store token in session ---
if "token" not in st.session_state:
    st.session_state.token = None

st.title("🔐 Login")

# --- Login Form ---
if st.session_state.token is None:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            try:
                res = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password}
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data.get("access_token")
                    st.success("✅ Logged in successfully!")
                else:
                    st.error(f"❌ Login failed: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- Chat + Voice UI (only visible when logged in) ---
if st.session_state.token:
    st.success("You are logged in ✅")

    # Tabs
    tab1, tab2 = st.tabs(["💬 Chatbot", "🎙️ Voice Agent"])

    # ---------------- CHAT TAB ----------------
    with tab1:
        st.subheader("💬 Chat with AI Tutor")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for role, msg in st.session_state.messages:
            st.chat_message(role).markdown(msg)

        if prompt := st.chat_input("Type your message..."):
            # Save user message
            st.session_state.messages.append(("user", prompt))
            st.chat_message("user").markdown(prompt)

            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                res = requests.post(
                    f"{API_URL}/chatbot/",
                    json={"message": prompt},
                    headers=headers
                )
                if res.status_code == 200:
                    reply = res.json().get("response", "⚠️ No reply")
                else:
                    reply = f"Error {res.status_code}: {res.text}"
            except Exception as e:
                reply = f"⚠️ Backend error: {e}"

            # Save + display reply
            st.session_state.messages.append(("assistant", reply))
            st.chat_message("assistant").markdown(reply)

    # ---------------- VOICE TAB ----------------
    with tab2:
        st.subheader("🎙️ Voice Interaction")

        # Record or upload audio
        audio_upload = st.audio_input("🎤 Record your voice")
        uploaded_file = st.file_uploader("Or upload a voice file", type=["wav", "mp3"])

        if (audio_upload or uploaded_file) and st.button("Send Voice"):
            with st.spinner("Processing voice..."):
                if audio_upload is not None:
                    files = {"file": ("recorded.wav", audio_upload, "audio/wav")}
                else:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    res = requests.post(
                        f"{API_URL}/voice/process",
                        files=files,
                        headers=headers
                    )

                    if res.status_code == 200:
                        result = res.json()
                        st.subheader("📝 AI Response")
                        st.write(result["text"])

                        # Decode & play TTS audio
                        audio_out = base64.b64decode(result["audio"])
                        st.subheader("🔊 AI Voice Reply")
                        st.audio(audio_out, format="audio/wav")
                    else:
                        st.error(f"Voice request failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
