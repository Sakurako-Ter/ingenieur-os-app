import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
from PIL import Image

# --- 1. CONFIGURATION SYSTÈME ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ GROQ_API_KEY manquante dans les Secrets Streamlit.")

# --- 2. DESIGN DARK MODE INDUSTRIEL ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #2e7bc4; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #1e5ba0; transform: scale(1.02); }
    .auth-box { padding: 20px; border: 1px solid #2e7bc4; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS TECHNIQUES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 4. AUTHENTIFICATION & PROFILS ---
if "auth_status" not in st.session_state:
    st.session_state.auth_status = False
    st.session_state.user_data = None

# ÉCRAN DE CONNEXION (Google / Apple)
if not st.session_status:
    st.title("🏗️ Ingénieur OS : Connexion Certifiée")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        if st.button("🔴 Se connecter avec Google"):
            st.session_state.auth_status = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        if st.button("⚫ Se connecter avec Apple"):
            st.session_state.auth_status = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ÉCRAN DE CONFIGURATION DU PROFIL
if st.session_state.auth_status and st.session_state.user_data is None:
    st.header("⚙️ Configuration de votre profil d'Ingénierie")
    with st.form("setup_profile"):
        nom = st.text_input("Nom complet ou Identifiant")
        statut = st.selectbox("Statut actuel :", [
            "Élève (Secondaire/Rhétos)", "Étudiant (Bachelier Ingénieur)", 
            "Étudiant (Master Ingénieur)", "Doctorant / Chercheur", 
            "Professionnel (Expert Métier)", "Professeur / Académique"
        ])
        entite = st.text_input("Université / École / Entreprise (ex: UCL, ULB, ArcelorMittal)")
        specialite = st.multiselect("Spécialités :", [
            "Génie Civil", "Électromécanique", "Chimie & Matériaux", 
            "Informatique & IA", "Physique Quantique", "Énergie & Environnement"
        ])
        
        if st.form_submit_button("Finaliser l'inscription"):
            if nom and entite:
                st.session_state.user_data = {"nom": nom, "statut": statut, "entite": entite, "spe": specialite}
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs.")
    st.stop()

# --- 5. NAVIGATION ---
st.sidebar.title(f"🚀 {st.session_state.user_data['nom']}")
st.sidebar.info(f"📍 {st.session_state.user_data['entite']}")
st.sidebar.caption(f"Spécialités : {', '.join(st.session_state.user_data['spe'])}")

menu = ["🔍 Recherche de Sources", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité"]
if "Expert" in st.session_state.user_data['statut'] or "Professeur" in st.session_state.user_data['statut']:
    menu.append("👑 Panel de Validation Expert")
menu.append("💎 Mode Premium")

choice = st.sidebar.radio("Navigation", menu)

# --- 6. PAGES ---

# PAGE RECHERCHE
if choice == "🔍 Recherche de Sources":
    st.title("📚 Moteur de Recherche Scientifique")
    query = st.text_input("Entrez un concept (ex: Calcul d'Eurocodes 3)")
    if query:
        with st.spinner("L'IA explore les bases académiques..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"Expert documentaliste. Cite des ouvrages, articles et thèses réels avec liens."},
                          {"role":"user","content":query}]
            )
            st.markdown(render_math(res.choices[0].message.content))

# PAGE IA (TEXTE / PHOTO / PDF)
elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-Supports")
    t1, t2, t3 = st.tabs(["📄 Texte", "📸 Photo / Schéma", "📂 Document PDF"])
    
    with tab2: # Vision
        img = st.file_uploader("Photo d'exercice :", type=['png', 'jpg', 'jpeg'])
        if img and st.button("Analyser Image"):
            b64 = base64.b64encode(img.getvalue()).decode('utf-8')
            res = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role":"user","content":[{"type":"text","text":"Explique en LaTeX."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}])
            st.markdown(render_math(res.choices[0].message.content))
    # ... (le reste du code PDF/Texte s'insère ici comme précédemment)

# PAGE RAPPORTS & BIBTEX (CONVERSATIONNEL)
elif choice == "📝 Rapports & BibTeX":
    st.title("📝 Copilote LaTeX & BibTeX")
    if "chat_latex" not in st.session_state: st.session_state.chat_latex = []
    
    for msg in st.session_state.chat_latex:
        with st.chat_message(msg["role"]): st.markdown(msg["content"]) if msg["role"]=="user" else st.code(msg["content"], language="latex")
    
    if inp := st.chat_input("Décrivez votre rapport ou demandez une modification..."):
        st.session_state.chat_latex.append({"role":"user","content":inp})
        with st.chat_message("user"): st.markdown(inp)
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert LaTeX. Donne UNIQUEMENT le code."}]+st.session_state.chat_latex)
        code = res.choices[0].message.content
        with st.chat_message("assistant"): st.code(code, language="latex")
        st.session_state.chat_latex.append({"role":"assistant","content":code})

# PAGE AUDIT DE FIABILITÉ
elif choice == "🛡️ Audit de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité")
    sujet = st.text_input("Sujet de votre travail :")
    source = st.text_area("Source (Lien ou Extrait) :")
    if st.button("Lancer l'audit scientifique"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Audit de fiabilité académique. Note sur 10."}, {"role":"user","content":f"Sujet: {sujet}\nSource: {source}"}])
        st.markdown(res.choices[0].message.content)
        if st.button("🚀 Soumettre pour certification aux experts"):
            st.success("Document envoyé dans la file d'attente des experts de votre secteur !")

# PAGE EXPERT (RÉSERVÉE)
elif choice == "👑 Panel de Validation Expert":
    st.title(f"👑 Centre de Certification : {st.session_state.user_data['spe'][0] if st.session_state.user_data['spe'] else 'Général'}")
    st.warning("📥 1 nouvelle source soumise par un étudiant (UCL)")
    st.code("Document : 'Étude de fatigue des métaux - Thèse Polytechnique'", language="markdown")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Valider et Certifier"): st.balloons()
    with c2:
        st.button("❌ Rejeter la source")

# PAGE PREMIUM
elif choice == "💎 Mode Premium":
    st.title("💎 Services Exclusifs Ingénieur OS")
    st.markdown("- **Planning de révision dynamique** (Mode Examen)\n- **IA Vision sans limites**\n- **Citations BibTeX automatiques**\n- **Accès prioritaire** aux documents certifiés")
    st.link_button("🚀 Activer l'abonnement (9,99€/mois)", "https://ton-lien-lemon-squeezy.com")
