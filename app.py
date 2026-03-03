import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
import os
from PIL import Image

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
    .block-container { padding-top: 1rem; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; }
    .hero-text { text-align: center; padding: 20px 0; }
    .feature-card { background-color: #1c1f26; padding: 20px; border-radius: 12px; border: 1px solid #2e7bc4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE D'ACCÈS & CONNEXION RAPIDE ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# --- PAGE D'ACCUEIL VITRINE ---
if st.session_state.user_profile is None and not st.session_state.show_register:
    st.markdown('<div class="hero-text"><h1>🏗️ INGÉNIEUR OS</h1><h3>L\'écosystème de réussite pour futurs ingénieurs.</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card">🔍 <b>Recherche</b><p>Sources académiques certifiées</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card">🤖 <b>IA Multimodale</b><p>Analyse Photo & PDF</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card">📝 <b>LaTeX</b><p>Copilote de rapports</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 ACCÉDER À LA PLATEFORME"):
        st.session_state.show_register = True
        st.rerun()

# --- FORMULAIRE D'ACCÈS (INSCRIPTION OU PIN) ---
elif st.session_state.user_profile is None and st.session_state.show_register:
    st.title("🏗️ Accès Ingénieur OS")
    
    tab_login, tab_reg = st.tabs(["🔑 Connexion rapide (Email + PIN)", "📝 Première inscription"])
    
    with tab_login:
        email_login = st.text_input("Adresse Email", key="email_log")
        pin_login = st.text_input("Code PIN", type="password", key="pin_log")
        if st.button("Entrer sur mon profil"):
            # Ici, pour un vrai système, on vérifierait dans une base de données
            # Pour l'instant, on simule une entrée réussie
            if email_login and pin_login:
                st.session_state.user_profile = {"nom": "Utilisateur", "role": "Étudiant", "entite": "Université", "detail": "Général"}
                st.rerun()

    with tab_reg:
        role = st.radio("Choisissez votre profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], horizontal=True)
        nom = st.text_input("Nom d'utilisateur / Pseudo")
        email_reg = st.text_input("Adresse Email", key="email_reg")
        pin_reg = st.text_input("Créez un Code PIN (4 chiffres)", type="password")

        detail_final = ""
        entite_nom = ""

        if role == "Élève (Secondaire)":
            entite_nom = st.text_input("École")
            option = st.selectbox("Option :", ["Math Fortes", "Sciences", "Technique", "Autre"])
            detail_final = st.text_input("Précisez votre option :") if option == "Autre" else option
        elif role == "Étudiant (Université)":
            entite_nom = st.text_input("Université (UCL, ULB, Liège...)")
            fac = st.selectbox("Faculté :", ["Polytech", "Sciences", "Architecture", "Autre"])
            detail_final = st.text_input("Précisez votre filière :") if fac == "Autre" else fac
        elif role == "Professionnel / Expert":
            entite_nom = st.text_input("Entreprise / Institution")
            expertise = st.selectbox("Expertise :", ["Génie Civil", "Électromécanique", "IA/Data", "Autre"])
            detail_final = st.text_input("Précisez votre spécialité :") if expertise == "Autre" else expertise
            linkedin = st.text_input("Lien LinkedIn (Vérification IA)")

        if st.button("Créer mon compte et Entrer"):
            if nom and email_reg and pin_reg and detail_final:
                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite_nom, "detail": detail_final}
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs.")

# --- 4. NAVIGATION (DASHBOARD) ---
if st.session_state.user_profile:
    st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
    st.sidebar.info(f"Profil : {st.session_state.user_profile['role']}")
    st.sidebar.caption(f"📍 {st.session_state.user_profile['entite']} ({st.session_state.user_profile['detail']})")

    menu = ["🔍 Recherche de Sources", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité", "💎 Mode Premium"]
    choice = st.sidebar.radio("Navigation", menu)

    def render_math(text):
        return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

    # --- 5. LOGIQUE DES PAGES ---
    if choice == "🔍 Recherche de Sources":
        st.title("📚 Moteur de Recherche Scientifique")
        q = st.text_input(f"Sujet lié à {st.session_state.user_profile['detail']} :")
        if q:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Donne des sources pour {q}."}])
            st.markdown(render_math(res.choices[0].message.content))

    elif choice == "🤖 Assistant IA Multi":
        st.title("🤖 Assistant IA Multimodal")
        up = st.file_uploader("Upload Image ou PDF", type=['png', 'jpg', 'pdf'])
        if up and st.button("Analyser"):
            st.info("Analyse en cours...")

    elif choice == "📝 Rapports & BibTeX":
        st.title("📝 Copilote LaTeX Conversationnel")
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        if inp := st.chat_input("Décrivez votre rapport..."):
            st.session_state.chat_history.append({"role":"user","content":inp})
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert LaTeX."}]+st.session_state.chat_history)
            st.code(res.choices[0].message.content, language="latex")

    elif choice == "🛡️ Audit de Fiabilité":
        st.title("🛡️ Analyseur de Fiabilité")
        st.write("Analyse des sources...")

    elif choice == "💎 Mode Premium":
        st.title("💎 Mode Premium")
        st.link_button("🚀 S'abonner (9,99€ / mois)", "https://votre-boutique.lemonsqueezy.com")
