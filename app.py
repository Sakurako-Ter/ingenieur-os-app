import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
import os

# --- 1. CONFIGURATION SYSTÈME ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .hero-text { text-align: center; padding: 30px 0; }
    .feature-card { background-color: #1c1f26; padding: 20px; border-radius: 12px; border: 1px solid #2e7bc4; text-align: center; margin-bottom: 20px; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; border: none; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTION DE LA SESSION ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- 4. LOGIQUE D'ACCÈS ---

# A. PAGE D'ACCUEIL VITRINE
if st.session_state.user_profile is None and st.session_state.page == "home":
    st.markdown('<div class="hero-text"><h1>🏗️ INGÉNIEUR OS</h1><h3>L\'écosystème de réussite certifié pour ingénieurs.</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card">🔍 <b>Recherche</b><p>Sources académiques certifiées</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card">🤖 <b>IA Multimodale</b><p>Analyse Photo & PDF</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card">📝 <b>LaTeX</b><p>Copilote de rapports pro</p></div>', unsafe_allow_html=True)
    
    if st.button("🚀 ACCÉDER À LA PLATEFORME"):
        st.session_state.page = "auth"
        st.rerun()

# B. PAGE D'AUTHENTIFICATION
elif st.session_state.user_profile is None and st.session_state.page == "auth":
    st.title("🏗️ Authentification Ingénieur OS")
    tab_login, tab_reg = st.tabs(["🔐 Connexion", "📝 Créer un compte"])

    with tab_login:
        email_log = st.text_input("Email", key="email_log")
        pw_log = st.text_input("Mot de passe", type="password", key="pw_log")
        if st.button("Se connecter"):
            if email_log and pw_log:
                st.session_state.user_profile = {"nom": "Utilisateur", "role": "Étudiant", "entite": "Université", "detail": "Général", "email": email_log}
                st.rerun()
            else:
                st.error("Veuillez remplir les identifiants.")

    with tab_reg:
        with st.form("registration_form"):
            st.subheader("Rejoindre le réseau")
            role = st.radio("Votre profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], horizontal=True)
            nom_reg = st.text_input("Nom complet / Pseudo")
            email_reg = st.text_input("Adresse Email")
            pw_reg = st.text_input("Créer un mot de passe sécurisé", type="password")

            # Initialisation des variables dynamiques
            entite_nom = st.text_input("École / Université / Entreprise")
            
            # Utilisation de colonnes pour les sélections précises
            detail_final = st.text_input("Spécialité / Option / Faculté précise")
            
            # LE BOUTON EST ICI, À L'INTÉRIEUR DU FORMULAIRE
            submitted = st.form_submit_button("Créer mon compte")
            
            if submitted:
                if nom_reg and email_reg and pw_reg and detail_final:
                    st.session_state.user_profile = {"nom": nom_reg, "role": role, "entite": entite_nom, "detail": detail_final, "email": email_reg}
                    st.success("Compte créé avec succès !")
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs.")
    
    if st.button("⬅️ Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()

# C. INTERFACE PRINCIPALE
elif st.session_state.user_profile:
    st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
    st.sidebar.info(f"Profil : {st.session_state.user_profile['role']}")
    
    menu = ["🔍 Recherche Certifiée", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "💎 Premium"]
    choice = st.sidebar.radio("Navigation", menu)

    def render_math(text):
        return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

    if choice == "🔍 Recherche Certifiée":
        st.title("📚 Moteur de Recherche Scientifique")
        q = st.text_input("Sujet :")
        if q:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Donne des sources pour {q}."}])
            st.markdown(render_math(res.choices[0].message.content))

    elif choice == "🤖 Assistant IA Multi":
        st.title("🤖 Assistant IA Multimodal")
        up = st.file_uploader("Upload Image ou PDF", type=['png', 'jpg', 'pdf'])
        if up: st.info("Fichier chargé. Utilisez l'IA pour l'analyser.")

    elif choice == "💎 Premium":
        st.title("💎 Mode Premium")
        st.link_button("🚀 S'abonner (9,99€/mois)", "https://votre-boutique.lemonsqueezy.com")
