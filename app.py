import streamlit as st
from groq import Groq
import base64
import PyPDF2
import io
import uuid

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Clé API manquante dans les Secrets Streamlit.")

# --- 2. GESTION DES SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {} 
if "current_sid" not in st.session_state:
    sid = str(uuid.uuid4())
    st.session_state.sessions[sid] = {"title": "Nouvelle discussion", "messages": []}
    st.session_state.current_sid = sid

# --- 3. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .home-card { background-color: #1e2130; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7bc4; margin-bottom: 15px; }
    .main-title { font-size: 3rem; font-weight: bold; color: #2e7bc4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def render_math(text):
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$") if text else ""

def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    return " ".join([p.extract_text() for p in reader.pages[:5]])

def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {"title": "Nouvelle discussion", "messages": []}
    st.session_state.current_sid = new_id
    st.rerun()

# --- 5. BARRE LATÉRALE (HISTORIQUE UNIQUEMENT) ---
with st.sidebar:
    st.title("🚀 Ingénieur OS")
    st.markdown("### 📜 Historique")
    for sid in list(st.session_state.sessions.keys()):
        col_t, col_d = st.columns([0.8, 0.2])
        with col_t:
            if st.button(st.session_state.sessions[sid]["title"][:20]+"...", key=f"s_{sid}", use_container_width=True):
                st.session_state.current_sid = sid
                st.rerun()
        with col_d:
            if st.button("🗑️", key=f"d_{sid}"):
                del st.session_state.sessions[sid]
                if not st.session_state.sessions: create_new_chat()
                elif st.session_state.current_sid == sid:
                    st.session_state.current_sid = list(st.session_state.sessions.keys())[0]
                st.rerun()
    st.markdown("---")
    choice = st.radio("Navigation", ["🏠 Accueil", "🤖 Assistant IA", "🔍 Recherche Arana", "📝 Rapports LaTeX"])

# --- 6. LOGIQUE DES PAGES ---

if choice == "🏠 Accueil":
    st.markdown('<h1 class="main-title">🏗️ Ingénieur OS</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Système expert pour Polytechnique.</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="home-card"><h3>🤖 Assistant IA</h3><p>Chat, PDF et Vision réunis en un seul flux.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="home-card"><h3>📝 Rapports</h3><p>Générateur de templates LaTeX.</p></div>', unsafe_allow_html=True)
    if st.button("🚀 Ouvrir l'Assistant"):
        st.session_state.choice = "🤖 Assistant IA" # Note: pour forcer le changement
        st.rerun()

elif choice == "🤖 Assistant IA":
    session = st.session_state.sessions[st.session_state.current_sid]
    
    # Header avec bouton Nouvelle Conversation sur la page
    col_title, col_new = st.columns([0.8, 0.2])
    with col_title:
        st.title(f"💬 {session['title']}")
    with col_new:
        if st.button("➕ Nouveau", use_container_width=True):
            create_new_chat()

    # Zone d'upload (Photo ou PDF)
    uploaded_file = st.file_uploader("Scanner un exercice (Photo) ou un syllabus (PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

    # Affichage des messages
    for msg in session["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(render_math(msg["content"]))

    # Chat Input
    if prompt := st.chat_input("Posez votre question ou expliquez le fichier joint..."):
        if not session["messages"]: session["title"] = prompt[:25]
        
        content_payload = []
        text_context = ""

        # Traitement du fichier joint
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                text_context = f"\n[Document PDF]: {extract_pdf_text(uploaded_file)}\n"
            else:
                # Si c'est une image, on utilise le modèle Vision
                b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                content_payload = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]

        # Ajout du message utilisateur
        user_text = text_context + prompt
        session["messages"].append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(prompt)
            if uploaded_file and "image" in uploaded_file.type: st.image(uploaded_file, width=300)

        # Réponse IA
        with st.chat_message("assistant"):
            try:
                model = "llama-3.2-11b-vision-preview" if content_payload else "llama-3.3-70b-versatile"
                messages_input = [{"role": "system", "content": "Ingénieur expert. LaTeX obligatoire."}] + session["messages"]
                
                # Si c'est une image, on remplace le dernier message par le format vision
                if content_payload:
                    messages_input[-1] = {"role": "user", "content": content_payload}

                res = client.chat.completions.create(model=model, messages=messages_input)
                ans = res.choices[0].message.content
                st.markdown(render_math(ans))
                session["messages"].append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"Erreur : {e}")

elif choice == "🔍 Recherche Arana":
    st.title("📚 Recherche Arana")
    q = st.text_input("Sujet :")
    if q:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Sources pour {q}"}])
        st.write(res.choices[0].message.content)

elif choice == "📝 Rapports LaTeX":
    st.title("📝 Générateur LaTeX")
    t = st.text_area("Sujet du rapport :")
    if st.button("Générer"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Code LaTeX pour {t}"}])
        st.code(res.choices[0].message.content, language="latex")
