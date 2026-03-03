import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io

# --- 1. CONFIGURATION ET CONNEXION IA ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

# Gestion de la clé API via les secrets Streamlit
# Documentation : https://docs.streamlit.io
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.warning("⚠️ Clé API manquante. Configurez GROQ_API_KEY dans vos secrets.")

# --- 2. DESIGN & STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2e7bc4; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1e5ba0; border: 1px solid white; }
    .home-card {
        background-color: #1e2130;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #2e7bc4;
        margin-bottom: 20px;
        height: 200px;
    }
    .main-title { font-size: 3rem; font-weight: bold; color: #2e7bc4; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS UTILES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 4. BARRE LATÉRALE (MENU) ---
st.sidebar.title("🚀 Ingénieur OS")
st.sidebar.markdown("---")
menu = ["🏠 Accueil", "🔍 Recherche Arana", "🤖 Assistant IA Multi", "📝 Rapports LaTeX", "🛡️ Analyse de Fiabilité", "💳 Version Premium"]
choice = st.sidebar.radio("Navigation", menu)
st.sidebar.markdown("---")
st.sidebar.caption("Plateforme pour le Bac 1 Ingénieur Civil.")

# --- 5. LOGIQUE DES PAGES ---

# --- PAGE ACCUEIL ---
if choice == "🏠 Accueil":
    st.markdown('<h1 class="main-title">🏗️ Ingénieur OS</h1>', unsafe_allow_html=True)
    st.subheader("Le système d'exploitation ultime pour votre réussite académique.")
    st.write("Conçu spécifiquement pour les défis du premier bloc polytechnique.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="home-card">
            <h3>🔍 Recherche Arana</h3>
            <p>Trouvez des sources certifiées, des ouvrages classiques et des articles scientifiques pour vos recherches et projets.</p>
        </div>
        <div class="home-card">
            <h3>🤖 Assistant IA Multi</h3>
            <p>Analysez vos énoncés, photos d'examens ou syllabus PDF. Réponse instantanée avec formules LaTeX.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="home-card">
            <h3>📝 Rapports LaTeX</h3>
            <p>Générez des structures de documents scientifiques propres et conformes aux exigences académiques.</p>
        </div>
        <div class="home-card">
            <h3>🛡️ Analyse de Fiabilité</h3>
            <p>Passez vos sources au crible de l'audit scientifique pour garantir l'intégrité de vos travaux.</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Démarrer une session de travail"):
        st.balloons()
        st.info("Sélectionnez un outil dans le menu à gauche pour commencer.")

# --- PAGE 1 : RECHERCHE (ARANA) ---
elif choice == "🔍 Recherche Arana":
    st.title("📚 Moteur de Recherche de Sources Certifiées")
    query = st.text_input("Sujet scientifique (ex: Thermodynamique des systèmes ouverts)", placeholder="Entrez un concept...")
    
    if query:
        with st.spinner("Exploration des bases académiques..."):
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Documentaliste expert. Donne 2 livres, 2 articles et liens Scholar. Utilise LaTeX."},
                        {"role": "user", "content": f"Recherche : {query}"}
                    ]
                )
                st.markdown(render_math(res.choices[0].message.content))
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- PAGE 2 : ASSISTANT IA ---
elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    tab1, tab2, tab3 = st.tabs(["📄 Texte", "📸 Photo", "📂 PDF"])

    with tab1:
        txt = st.text_area("Énoncé :", height=150)
        if st.button("Analyser"):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"Tuteur ingénieur. LaTeX requis."}, {"role":"user","content":txt}]
            )
            st.markdown(render_math(res.choices[0].message.content))

    with tab2:
        img = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        if img and st.button("Scanner l'image"):
            b64 = base64.b64encode(img.getvalue()).decode('utf-8')
            res = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role":"user","content":[
                    {"type":"text","text":"Explique cet exercice en LaTeX."},
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                ]}]
            )
            st.markdown(render_math(res.choices[0].message.content))

    with tab3:
        pdf = st.file_uploader("Upload PDF", type=['pdf'])
        if pdf and st.button("Extraire & Analyser"):
            reader = PyPDF2.PdfReader(pdf)
            content = "".join([p.extract_text() for p in reader.pages[:3]])
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"user","content":f"Analyse ce PDF : {content[:4000]}"}]
            )
            st.markdown(render_math(res.choices[0].message.content))

# --- PAGE 3 : RAPPORTS LATEX ---
elif choice == "📝 Rapports LaTeX":
    st.title("📝 Copilote LaTeX")
    if "latex_chat" not in st.session_state:
        st.session_state.latex_chat = []

    for msg in st.session_state.latex_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Décris le rapport souhaité..."):
        st.session_state.latex_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        with st.chat_message("assistant"):
            messages = [{"role": "system", "content": "Expert LaTeX. Donne le code complet."}] + st.session_state.latex_chat
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
            ans = res.choices[0].message.content
            st.code(ans, language="latex")
            st.session_state.latex_chat.append({"role": "assistant", "content": ans})

# --- PAGE 4 : ANALYSE DE FIABILITÉ ---
elif choice == "🛡️ Analyse de Fiabilité":
    st.title("🛡️ Audit de Fiabilité")
    doc_content = st.text_area("Contenu de la source :", height=200)
    if st.button("Lancer l'audit"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"Analyse la scientificité sur 10."}, {"role":"user","content":doc_content}]
        )
        st.markdown(res.choices[0].message.content)

# --- PAGE 5 : PREMIUM ---
elif choice == "💳 Version Premium":
    st.title("💳 Passez au niveau supérieur")
    st.success("Accès illimité aux modèles Llama 3 Vision et export PDF direct.")
    st.button("S'abonner (Prochainement)")
