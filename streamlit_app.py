import streamlit as st 
import requests
import base64

API_URL = "http://127.0.0.1:8000"  # FastAPI backend

st.set_page_config(page_title="AI Chatbot + Voice + Upload", layout="wide")

# --- Store token in session ---
if "token" not in st.session_state:
    st.session_state.token = None

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔐 AI Tutor Auth & Chat")

# --- Tabs for Register/Login ---
tab1, tab2 = st.tabs(["Login", "Register"])

# ---------------- LOGIN ----------------
with tab1:
    st.subheader("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        try:
            res = requests.post(
                f"{API_URL}/auth/login",
                json={"email": login_email, "password": login_password}
            )
            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data.get("access_token")
                st.success("✅ Logged in successfully!")
            else:
                st.error(f"❌ Login failed: {res.json().get('detail')}")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- REGISTER ----------------
with tab2:
    st.subheader("Register")
    reg_email = st.text_input("Email", key="reg_email")
    reg_username = st.text_input("Username", key="reg_username")
    reg_password = st.text_input("Password", type="password", key="reg_password")
    
    if st.button("Register"):
        try:
            res = requests.post(
                f"{API_URL}/auth/register",
                json={"email": reg_email, "username": reg_username, "password": reg_password}
            )
            if res.status_code == 200:
                st.success("✅ Registration successful! You can now log in.")
            else:
                st.error(f"❌ Registration failed: {res.json().get('detail')}")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- LOGGED IN TABS ----------------
if st.session_state.token:
    st.success("You are logged in ✅")

    chat_tab, voice_tab, upload_tab = st.tabs(["💬 Chatbot", "🎙️ Voice Agent", "📄 Upload File"])

    # ---------------- CHAT TAB ----------------
    with chat_tab:
        st.subheader("💬 Chat with AI Tutor")

        for role, msg in st.session_state.messages:
            st.chat_message(role).markdown(msg)

        if prompt := st.chat_input("Type your message..."):
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
                    data = res.json()
                    reply = data.get("response", "⚠️ No reply")

                    # --- NEW: show orchestrator decision ---
                    decision = data.get("decision")
                    if decision:
                        reply += f"\n\n🤖 *Orchestrator chose*: `{decision}`"

                    # --- Optional: show raw state for debugging ---
                    if st.checkbox("Show raw state (debug)"):
                        st.json(data.get("raw_state", {}))

                else:
                    reply = f"Error {res.status_code}: {res.text}"
            except Exception as e:
                reply = f"⚠️ Backend error: {e}"

            st.session_state.messages.append(("assistant", reply))
            st.chat_message("assistant").markdown(reply)

    # ---------------- VOICE TAB ----------------
    with voice_tab:
        st.subheader("🎙️ Voice Interaction")

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

                        audio_out = base64.b64decode(result["audio"])
                        st.subheader("🔊 AI Voice Reply")
                        st.audio(audio_out, format="audio/wav")
                    else:
                        st.error(f"Voice request failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ---------------- UPLOAD TAB ----------------
    with upload_tab:
        st.subheader("📄 Upload File for Embedding")
        file_to_upload = st.file_uploader("Select a file", type=["pdf", "txt", "docx"])

        if file_to_upload and st.button("Upload File"):
            with st.spinner("Uploading and processing file..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    files = {"file": (file_to_upload.name, file_to_upload, file_to_upload.type)}
                    
                    # ✅ Corrected URL with double /tutor prefix
                    res = requests.post(
                        f"{API_URL}/tutor/tutor/upload",
                        files=files,
                        headers=headers
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"✅ {data['message']}")
                        st.info(f"Chunks created: {data['num_chunks']}")
                    else:
                        st.error(f"❌ Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
