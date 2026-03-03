import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io

# --- 1. CONFIGURATION ET CONNEXION IA ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. DESIGN & STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2e7bc4; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1e5ba0; border: 1px solid white; }
    div.stDataFrame { border-radius: 10px; overflow: hidden; }
    .stChatInput { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS UTILES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 4. BARRE LATÉRALE (MENU) ---
st.sidebar.title("🚀 Ingénieur OS")
st.sidebar.markdown("---")
menu = ["🔍 Recherche Arana", "🤖 Assistant IA Multi", "📝 Rapports LaTeX", "💳 Version Premium"]
choice = st.sidebar.radio("Navigation", menu)
st.sidebar.markdown("---")
st.sidebar.caption("Plateforme révolutionnaire pour le Bac 1 Ingénieur Civil.")

# --- 5. LOGIQUE DES PAGES ---

# --- PAGE 1 : RECHERCHE (ARANA) ---
if choice == "🔍 Recherche Arana":
    st.title("📚 Moteur de Recherche de Sources Certifiées")
    st.write("Trouvez des références académiques (articles, thèses, ouvrages) pour vos rapports.")
    
    query = st.text_input("Sujet scientifique (ex: Résistance des matériaux)", placeholder="Entrez un concept précis...")
    
    if query:
        with st.spinner("L'IA explore les bases de données académiques..."):
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": """Tu es un documentaliste expert. 
                        Pour le sujet donné, donne :
                        1. 📖 OUVRAGES : 2 livres classiques.
                        2. 🎓 THÈSES/ARTICLES : 2 ou 3 titres réels.
                        3. 🔗 LIENS : Liens cliquables vers Google Scholar/ResearchGate.
                        Réponds en LaTeX pour les formules."""},
                        {"role": "user", "content": f"Recherche approfondie : {query}"}
                    ]
                )
                
                st.markdown("### 🎯 Résultats de la recherche :")
                # LE [0] EST ICI POUR ÉVITER L'ERREUR
                st.markdown(render_math(res.choices[0].message.content))
                
            except Exception as e:
                st.error(f"Erreur de recherche : {e}")


# --- PAGE 2 : ASSISTANT IA (TEXTE, PHOTO, PDF) ---
elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    tab1, tab2, tab3 = st.tabs(["📄 Texte", "📸 Photo / Schéma", "📂 Document PDF"])

    with tab1:
        txt = st.text_area("Énoncé du problème :", height=150, placeholder="Ex: Comment calculer la flèche d'une poutre ?")
        if st.button("Analyser le texte"):
            with st.spinner("Réflexion..."):
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"system","content":"Tuteur ingénieur. Réponds en LaTeX."}, {"role":"user","content":txt}]
                )
                st.markdown(render_math(res.choices[0].message.content))

    with tab2:
        img = st.file_uploader("Photo de l'exercice :", type=['png', 'jpg', 'jpeg'])
        if img:
            st.image(img, width=400)
            if st.button("Analyser la photo"):
                with st.spinner("L'IA examine l'image..."):
                    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role":"user","content":[
                            {"type":"text","text":"Analyse cet exercice et explique la méthode en LaTeX."},
                            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                    st.markdown(render_math(res.choices[0].message.content))

    with tab3:
        pdf = st.file_uploader("Syllabus ou Examen (PDF) :", type=['pdf'])
        if pdf and st.button("Analyser le PDF"):
            with st.spinner("Lecture du PDF..."):
                reader = PyPDF2.PdfReader(pdf)
                content = "".join([p.extract_text() for p in reader.pages[:3]])
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"user","content":f"Analyse ce contenu de PDF d'ingénieur et réponds aux questions en LaTeX: {content[:5000]}"}]
                )
                st.markdown(render_math(res.choices[0].message.content))

# --- PAGE 3 : RAPPORTS LATEX (CONVERSATIONNEL) ---
elif choice == "📝 Rapports LaTeX":
    st.title("📝 Copilote LaTeX Conversationnel")
    st.info("Explique ton projet (ex: 'Fais-moi un rapport de physique').")

    # Initialisation de la mémoire dans la session
    if "latex_chat" not in st.session_state:
        st.session_state.latex_chat = []

    # Affichage des messages
    for msg in st.session_state.latex_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de saisie
    if user_input := st.chat_input("Décris ton rapport ici..."):
        st.session_state.latex_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                # Appel IA
                messages = [{"role": "system", "content": "Expert LaTeX. Donne le code complet."}] + st.session_state.latex_chat
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
                full_code = res.choices.message.content
                
                st.code(full_code, language="latex")
                st.session_state.latex_chat.append({"role": "assistant", "content": full_code})
            except Exception as e:
                st.error(f"Erreur : {e}")


# --- PAGE 4 : PREMIUM ---
elif choice == "💳 Version Premium":
    st.title("💳 Passez au Niveau Premium")
    st.markdown("""
    ### Débloquez la puissance totale :
    - ✅ **Recherche illimitée** dans toutes les archives d'examens.
    - ✅ **IA Vision & PDF sans limites** (Analyse de documents complets).
    - ✅ **Accès aux corrigés détaillés** rédigés par des tuteurs.
    """)
    st.link_button("🚀 S'abonner (9,99€ / mois)", "https://www.lemonsqueezy.com")
