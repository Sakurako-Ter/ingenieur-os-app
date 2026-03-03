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
    st.error("⚠️ Erreur : Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. GESTION DES SESSIONS ET HISTORIQUE ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {}  # Format: {id: {"title": str, "messages": list}}

if "current_sid" not in st.session_state:
    # Créer une première session vide
    sid = str(uuid.uuid4())
    st.session_state.sessions[sid] = {"title": "Nouvelle discussion", "messages": []}
    st.session_state.current_sid = sid

# --- 3. DESIGN & STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #2e7bc4; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1e5ba0; border: 1px solid white; }
    .home-card {
        background-color: #1e2130; padding: 20px; border-radius: 15px;
        border-left: 5px solid #2e7bc4; margin-bottom: 20px; height: 180px;
    }
    .main-title { font-size: 3.5rem; font-weight: bold; color: #2e7bc4; text-align: center; }
    .sidebar-history { margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS UTILES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    return " ".join([p.extract_text() for p in reader.pages[:5]])

# --- 5. BARRE LATÉRALE (NAVIGATION & HISTORIQUE) ---
with st.sidebar:
    st.title("🚀 Ingénieur OS")
    
    # BOUTON NOUVELLE CONVERSATION (+)
    if st.button("➕ Nouvelle discussion", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"title": "Nouvelle discussion", "messages": []}
        st.session_state.current_sid = new_id
        st.rerun()

    st.markdown("### 📜 Historique")
    # Liste des conversations avec option de suppression
    for sid in list(st.session_state.sessions.keys()):
        col_t, col_d = st.columns([0.8, 0.2])
        with col_t:
            label = st.session_state.sessions[sid]["title"][:20] + "..."
            if st.button(label, key=f"sel_{sid}", use_container_width=True):
                st.session_state.current_sid = sid
                st.rerun()
        with col_d:
            if st.button("🗑️", key=f"del_{sid}"):
                del st.session_state.sessions[sid]
                if st.session_state.current_sid == sid:
                    remaining = list(st.session_state.sessions.keys())
                    st.session_state.current_sid = remaining[0] if remaining else None
                st.rerun()

    st.markdown("---")
    menu = ["🏠 Accueil", "🤖 Assistant IA Conversationnel", "🔍 Recherche Arana", "📝 Rapports LaTeX", "🛡️ Analyse de Fiabilité", "💳 Version Premium"]
    choice = st.sidebar.radio("Navigation", menu)

# --- 6. LOGIQUE DES PAGES ---

if choice == "🏠 Accueil":
    st.markdown('<h1 class="main-title">🏗️ Ingénieur OS</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>L'écosystème intelligent dédié à la réussite en Polytechnique.</p>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="home-card"><h3>🤖 Assistant Multi-Support</h3><p>Chat intelligent, analyse de photos et lecture de syllabus PDF.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="home-card"><h3>🔍 Recherche Arana</h3><p>Accédez à des sources académiques certifiées.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="home-card"><h3>📝 Rapports LaTeX</h3><p>Structures de rapports scientifiques prêtes à compiler.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="home-card"><h3>🛡️ Analyse de Fiabilité</h3><p>Vérifiez la rigueur de vos sources.</p></div>', unsafe_allow_html=True)

elif choice == "🤖 Assistant IA Conversationnel":
    if not st.session_state.current_sid:
        st.info("Cliquez sur ➕ pour commencer une discussion.")
    else:
        session = st.session_state.sessions[st.session_state.current_sid]
        st.title(f"🤖 {session['title']}")
        
        tab1, tab2, tab3 = st.tabs(["💬 Chat & Fichiers", "📸 Analyse Photo", "📂 Setup PDF"])

        with tab1:
            # Affichage historique
            for message in session["messages"]:
                with st.chat_message(message["role"]):
                    st.markdown(render_math(message["content"]))

            # Chat Input + Fichier
            with st.container():
                up_file = st.file_uploader("Joindre un document à ma question (Optionnel)", type=['pdf', 'txt'], key="chat_file")
                if prompt := st.chat_input("Posez votre question..."):
                    
                    # Contexte fichier si présent
                    context = ""
                    if up_file:
                        with st.spinner("Lecture du fichier..."):
                            if up_file.type == "application/pdf":
                                context = f"\n[DOCUMENT]: {extract_pdf_text(up_file)}\n\n"
                            else:
                                context = f"\n[DOCUMENT]: {up_file.read().decode()}\n\n"
                    
                    full_prompt = context + prompt
                    
                    # Update titre auto
                    if not session["messages"]:
                        session["title"] = prompt[:30]

                    session["messages"].append({"role": "user", "content": full_prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        res = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": "Expert ingénieur. Utilise LaTeX."}] + session["messages"]
                        )
                        ans = res.choices[0].message.content
                        st.markdown(render_math(ans))
                        session["messages"].append({"role": "assistant", "content": ans})

        with tab2:
            img = st.file_uploader("Photo de l'exercice :", type=['png', 'jpg', 'jpeg'])
            if img and st.button("Analyser l'image"):
                b64 = base64.b64encode(img.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{"role":"user","content":[{"type":"text","text":"Explique cet exercice en LaTeX."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]
                )
                analysis = res.choices[0].message.content
                session["messages"].append({"role": "assistant", "content": f"[Analyse Photo] : {analysis}"})
                st.markdown(render_math(analysis))

        with tab3:
            st.info("Le chargement de PDF est désormais intégré directement dans l'onglet 'Chat & Fichiers' pour plus de fluidité.")

elif choice == "🔍 Recherche Arana":
    st.title("📚 Recherche Arana")
    query = st.text_input("Sujet :")
    if query:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Sources pour {query}"}])
        st.markdown(render_math(res.choices[0].message.content))

elif choice == "📝 Rapports LaTeX":
    st.title("📝 Générateur LaTeX")
    req = st.text_area("Description :")
    if st.button("Générer"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Code LaTeX complet pour : {req}"}])
        st.code(res.choices[0].message.content, language="latex")

elif choice == "🛡️ Analyse de Fiabilité":
    st.title("🛡️ Audit")
    src = st.text_area("Texte :")
    if st.button("Vérifier"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Analyse la fiabilité : {src}"}])
        st.write(res.choices[0].message.content)

elif choice == "💳 Version Premium":
    st.title("💳 Premium")
    st.write("Bientôt disponible.")
