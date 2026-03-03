import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
from PIL import Image

# --- 1. CONFIGURATION ET CONNEXION ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. DESIGN & STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2e7bc4; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1e5ba0; border: 1px solid white; }
    .stChatInput { border-radius: 10px; }
    div.stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS UTILES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 4. SYSTÈME DE COMPTE ET AUTHENTIFICATION ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.user_profile is None:
    st.title("🔐 Bienvenue sur Ingénieur OS")
    st.subheader("Créez votre profil pour accéder à la plateforme")
    with st.form("login_form"):
        nom = st.text_input("Nom complet / Pseudonyme")
        role = st.selectbox("Votre profil :", ["Étudiant Université", "Élève Secondaire", "Professionnel / Expert"])
        secteur = "Général"
        if role == "Professionnel / Expert":
            secteur = st.selectbox("Votre domaine d'expertise :", 
                                 ["Génie Civil & Structures", "Électromécanique", "Informatique & IA", "Chimie & Matériaux"])
        
        if st.form_submit_button("Entrer sur la plateforme"):
            if nom:
                st.session_state.user_profile = {"nom": nom, "role": role, "secteur": secteur}
                st.rerun()
            else:
                st.error("Veuillez entrer un nom.")
    st.stop()

# --- 5. BARRE LATÉRALE (MENU) ---
st.sidebar.title(f"👋 {st.session_state.user_profile['nom']}")
st.sidebar.caption(f"Profil : {st.session_state.user_profile['role']}")
st.sidebar.markdown("---")

menu = ["🔍 Recherche de Sources", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité"]
if st.session_state.user_profile["role"] == "Professionnel / Expert":
    menu.append("✅ Validation Expert")
menu.append("💳 Version Premium")

choice = st.sidebar.radio("Navigation", menu)

# --- 6. LOGIQUE DES PAGES ---

# --- PAGE 1 : RECHERCHE ---
if choice == "🔍 Recherche de Sources":
    st.title("📚 Moteur de Recherche de Sources Fiables")
    query = st.text_input("Sujet de recherche :", placeholder="Ex: Analyse des contraintes d'une poutre...")
    if query:
        with st.spinner("L'IA cherche des sources académiques..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"Documentaliste expert. Donne : 1. Ouvrages clés. 2. Articles/Thèses réels. 3. Liens de recherche."},
                          {"role":"user","content":f"Trouve des sources fiables pour : {query}"}]
            )
            st.markdown(render_math(res.choices[0].message.content))

# --- PAGE 2 : ASSISTANT IA (TEXTE, PHOTO, PDF) ---
elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    tab1, tab2, tab3 = st.tabs(["📄 Texte", "📸 Photo / Schéma", "📂 Document PDF"])
    
    with tab1:
        txt = st.text_area("Énoncé :")
        if st.button("Analyser"):
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":txt}])
            st.markdown(render_math(res.choices[0].message.content))

    with tab2:
        img = st.file_uploader("Photo de l'exercice :", type=['png', 'jpg', 'jpeg'])
        if img and st.button("Analyser Image"):
            b64 = base64.b64encode(img.getvalue()).decode('utf-8')
            res = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role":"user","content":[{"type":"text","text":"Explique en LaTeX."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}])
            st.markdown(render_math(res.choices[0].message.content))

    with tab3:
        pdf = st.file_uploader("Syllabus (PDF) :", type=['pdf'])
        if pdf and st.button("Analyser PDF"):
            reader = PyPDF2.PdfReader(pdf)
            content = "".join([p.extract_text() for p in reader.pages[:3]])
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Analyse ce PDF d'ingénieur : {content[:5000]}"}])
            st.markdown(render_math(res.choices[0].message.content))

# --- PAGE 3 : RAPPORTS & BIBTEX ---
elif choice == "📝 Rapports & BibTeX":
    st.title("📝 Copilote LaTeX & BibTeX")
    t1, t2 = st.tabs(["💬 Conversationnel", "🔖 Générateur BibTeX"])
    
    with t1:
        if "latex_chat" not in st.session_state: st.session_state.latex_chat = []
        for m in st.session_state.latex_chat:
            with st.chat_message(m["role"]): st.markdown(m["content"]) if m["role"]=="user" else st.code(m["content"], language="latex")
        if inp := st.chat_input("Décrivez votre rapport..."):
            st.session_state.latex_chat.append({"role":"user","content":inp})
            with st.chat_message("user"): st.markdown(inp)
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert LaTeX. Donne UNIQUEMENT le code."}]+st.session_state.latex_chat)
            code = res.choices[0].message.content
            with st.chat_message("assistant"): st.code(code, language="latex")
            st.session_state.latex_chat.append({"role":"assistant","content":code})

    with t2:
        source = st.text_input("Titre ou Lien du document pour BibTeX :")
        if st.button("Générer la citation"):
            res = client.chat.get_completions(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Génère un bloc BibTeX pour : {source}"}])
            st.code(res.choices[0].message.content, language="latex")

# --- PAGE 4 : AUDIT DE FIABILITÉ ---
elif choice == "🛡️ Audit de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité")
    sujet = st.text_input("Sujet de recherche :")
    source_val = st.text_area("Contenu ou URL de la source :")
    if st.button("Lancer l'audit"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert en intégrité académique. Note sur 10."}, {"role":"user","content":f"Sujet: {sujet}\nSource: {source_val}"}])
        st.markdown(res.choices[0].message.content)
        if st.button("🚀 Soumettre aux Experts pour validation"):
            st.success("La source a été transmise aux experts de votre secteur !")

# --- PAGE 5 : VALIDATION EXPERT ---
elif choice == "✅ Validation Expert":
    st.title(f"🎯 Centre de Validation : {st.session_state.user_profile['secteur']}")
    st.info("Validez les sources soumises par les étudiants de votre domaine.")
    st.warning("📄 File d'attente : 'Impact des Eurocodes sur la résistance des bétons.pdf'")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Valider et certifier"): st.balloons()
    with c2:
        if st.button("❌ Rejeter"): st.error("Rejeté")

# --- PAGE 6 : PREMIUM ---
elif choice == "💳 Version Premium":
    st.title("💳 Mode Examen Premium")
    st.markdown("- **Planning de révision automatique** IA\n- **IA Vision illimitée**\n- **Priorité de validation** par les experts")
    st.link_button("S'abonner (9,99€ / mois)", "https://ton-lien-lemon-squeezy.com")
