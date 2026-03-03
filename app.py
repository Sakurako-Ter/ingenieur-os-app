import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
from PIL import Image

# --- 1. CONFIGURATION SYSTÈME ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

# Connexion à l'IA via Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ GROQ_API_KEY manquante dans les Secrets Streamlit.")

# --- 2. DESIGN PRO & DARK MODE ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .login-box { background-color: #1c1f26; padding: 50px; border-radius: 20px; border: 1px solid #2e7bc4; text-align: center; box-shadow: 0px 10px 30px rgba(0,0,0,0.5); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold; transition: 0.3s; }
    .stChatInput { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS TECHNIQUES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 4. VRAIE AUTHENTIFICATION (SIMULATION SSO) ---
if "auth_status" not in st.session_state:
    st.session_state.auth_status = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# ÉCRAN DE LOGIN "COMME LES AUTRES SITES"
if not st.session_state.auth_status:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("🏗️ Ingénieur OS")
    st.subheader("Connectez-vous pour accéder à votre espace certifié")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔴 Continuer avec Google"):
            st.session_state.auth_status = True
            st.rerun()
        if st.button("⚫ Continuer avec Apple"):
            st.session_state.auth_status = True
            st.rerun()
    
    st.markdown("---")
    st.caption("Plateforme sécurisée pour la réussite en Ingénierie Civile")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ÉCRAN DE CONFIGURATION DE PROFIL (APRES LOGIN)
if st.session_state.auth_status and st.session_state.user_data is None:
    st.title("🚀 Bienvenue ! Finalisons votre profil")
    with st.form("profile_setup"):
        nom = st.text_input("Nom & Prénom / Identifiant")
        statut = st.selectbox("Votre parcours :", [
            "Élève (Secondaire/Rhétos)", "Étudiant (Bachelier Ingénieur)", 
            "Étudiant (Master Ingénieur)", "Doctorant / Chercheur", 
            "Ingénieur Expert (Professionnel)", "Professeur / Académique"
        ])
        ecole = st.text_input("Université ou Entreprise (ex: UCL, ULB, Liège, Arcelor...)")
        
        # Variété des secteurs selon le profil
        secteur = st.selectbox("Secteur principal :", [
            "Structures & Génie Civil", "Électromécanique", "Informatique & IA", 
            "Chimie & Matériaux", "Énergie", "Physique Fondamentale"
        ])
        
        if st.form_submit_button("Accéder au Dashboard"):
            if nom and ecole:
                st.session_state.user_data = {"nom": nom, "statut": statut, "ecole": ecole, "secteur": secteur}
                st.rerun()
            else:
                st.error("Tous les champs sont obligatoires.")
    st.stop()

# --- 5. INTERFACE PRINCIPALE (DASHBOARD) ---
st.sidebar.title(f"👨‍💻 {st.session_state.user_data['nom']}")
st.sidebar.info(f"🏫 {st.session_state.user_data['ecole']}")
st.sidebar.caption(f"Secteur : {st.session_state.user_data['secteur']}")

menu = ["🔍 Recherche de Sources", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité"]
# L'onglet expert n'apparaît que pour les pros
if "Expert" in st.session_state.user_data['statut'] or "Professeur" in st.session_state.user_data['statut']:
    menu.append("👑 Panel de Validation Expert")
menu.append("💎 Mode Premium")

choice = st.sidebar.radio("Navigation", menu)

# --- 6. LOGIQUE DES PAGES ---

# PAGE 1 : RECHERCHE
if choice == "🔍 Recherche de Sources":
    st.title("📚 Moteur de Recherche Scientifique")
    query = st.text_input("Sujet de recherche (ex: Seconde loi de la thermodynamique)")
    if query:
        with st.spinner("Recherche de sources fiables..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"Documentaliste expert. Donne 2 livres, 2 thèses/articles et pourquoi ils sont fiables."},
                          {"role":"user","content":query}]
            )
            st.markdown(render_math(res.choices.message.content))

# PAGE 2 : ASSISTANT IA (PHOTO / PDF / TEXTE)
elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    t1, t2, t3 = st.tabs(["📄 Texte", "📸 Photo / Schéma", "📂 Document PDF"])
    
    with t2:
        img = st.file_uploader("Photo d'exercice :", type=['png', 'jpg', 'jpeg'])
        if img and st.button("Analyser Image"):
            b64 = base64.b64encode(img.getvalue()).decode('utf-8')
            res = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role":"user","content":[{"type":"text","text":"Explique en LaTeX."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}])
            st.markdown(render_math(res.choices.message.content))
    
    with t3:
        pdf = st.file_uploader("Upload PDF :", type=['pdf'])
        if pdf and st.button("Analyser PDF"):
            reader = PyPDF2.PdfReader(pdf)
            text = "".join([p.extract_text() for p in reader.pages[:3]])
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Analyse ce PDF: {text[:5000]}"}])
            st.markdown(render_math(res.choices.message.content))

# PAGE 3 : RAPPORTS & BIBTEX (CONVERSATIONNEL)
elif choice == "📝 Rapports & BibTeX":
    st.title("📝 Copilote LaTeX Conversationnel")
    if "chat_latex" not in st.session_state: st.session_state.chat_latex = []
    for m in st.session_state.chat_latex:
        with st.chat_message(m["role"]): st.markdown(m["content"]) if m["role"]=="user" else st.code(m["content"], language="latex")
    if inp := st.chat_input("Décrivez votre rapport ou demandez une modification..."):
        st.session_state.chat_latex.append({"role":"user","content":inp})
        with st.chat_message("user"): st.markdown(inp)
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert LaTeX. Donne UNIQUEMENT le code."}]+st.session_state.chat_latex)
        code = res.choices.message.content
        with st.chat_message("assistant"): st.code(code, language="latex")
        st.session_state.chat_latex.append({"role":"assistant","content":code})

# PAGE 4 : AUDIT DE FIABILITÉ
elif choice == "🛡️ Audit de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité")
    sujet = st.text_input("Sujet de votre travail :")
    source = st.text_area("Source (Lien ou Extrait) :")
    if st.button("Lancer l'audit scientifique"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Audit de fiabilité académique. Note sur 10."}, {"role":"user","content":f"Sujet: {sujet}\nSource: {source}"}])
        st.markdown(res.choices.message.content)
        if st.button("🚀 Soumettre pour certification aux experts"):
            st.success("Document envoyé dans la file d'attente des experts de votre secteur !")

# PAGE 5 : VALIDATION EXPERT
elif choice == "👑 Panel de Validation Expert":
    st.title(f"👑 Centre de Certification : {st.session_state.user_data['secteur']}")
    st.warning("📥 1 nouvelle source soumise par un étudiant (UCL)")
    st.code("Document : 'Étude de fatigue des métaux - Thèse Polytechnique'", language="markdown")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Valider et Certifier"): st.balloons()
    with c2:
        st.button("❌ Rejeter la source")

# PAGE 6 : PREMIUM
elif choice == "💎 Mode Premium":
    st.title("💎 Services Exclusifs Ingénieur OS")
    st.markdown("- **Mode Examen** (Planning de révision dynamique)\n- **IA Vision sans limites**\n- **Accès prioritaire** aux documents certifiés")
    st.link_button("🚀 Activer l'abonnement (9,99€/mois)", "https://votre-boutique.lemonsqueezy.com...")
