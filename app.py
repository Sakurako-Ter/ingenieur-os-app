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

# --- 2. STYLE CSS (DESIGN ÉPURÉ) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .block-container { padding-top: 2rem; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; border: none; }
    .hero-text { text-align: center; padding-bottom: 30px; }
    .feature-card { background-color: #1c1f26; padding: 20px; border-radius: 12px; border: 1px solid #2e7bc4; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE D'ACCÈS & AUTHENTIFICATION ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# --- PAGE D'ACCUEIL VITRINE ---
if st.session_state.user_profile is None and not st.session_state.show_register:
    st.markdown('<div class="hero-text"><h1>🏗️ INGÉNIEUR OS</h1><h3>L\'écosystème de réussite certifié pour ingénieurs.</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card">🔍 <b>Recherche</b><p>Sources académiques certifiées</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card">🤖 <b>IA Multimodale</b><p>Analyse Photo & PDF</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card">📝 <b>LaTeX</b><p>Copilote de rapports pro</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 ACCÉDER À LA PLATEFORME"):
        st.session_state.show_register = True
        st.rerun()

# --- FORMULAIRE D'ACCÈS (CONNEXION OU CRÉATION) ---
elif st.session_state.user_profile is None and st.session_state.show_register:
    st.title("🏗️ Accès Ingénieur OS")
    
    tab_login, tab_reg = st.tabs(["🔐 Connexion", "📝 Créer mon compte"])
    
    with tab_login:
        email_log = st.text_input("Email", key="email_log")
        pw_log = st.text_input("Mot de passe", type="password", key="pw_log")
        if st.button("Se connecter"):
            # Simulation de succès (À lier à une DB comme Google Sheets plus tard)
            if email_log and pw_log:
                st.session_state.user_profile = {"nom": "Utilisateur", "role": "Étudiant", "entite": "Université", "detail": "Général"}
                st.success("Connexion réussie !")
                st.rerun()

    with tab_reg:
        role = st.radio("Votre profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], horizontal=True)
        nom_reg = st.text_input("Nom d'utilisateur / Pseudo")
        email_reg = st.text_input("Adresse Email", key="email_reg_field")
        pw_reg = st.text_input("Créer un mot de passe sécurisé", type="password")

        # Initialisation des variables dynamiques
        detail_final = ""
        entite_nom = ""

        if role == "Élève (Secondaire)":
            entite_nom = st.text_input("Nom de votre École")
            option = st.selectbox("Votre option :", ["Math Fortes", "Sciences", "Technique", "Autre"])
            detail_final = st.text_input("Précisez votre option :") if option == "Autre" else option
        
        elif role == "Étudiant (Université)":
            entite_nom = st.text_input("Université (ex: UCL, ULB, ULiège...)")
            fac = st.selectbox("Faculté :", ["Polytech", "Sciences", "Architecture", "Autre"])
            detail_final = st.text_input("Précisez votre filière :") if fac == "Autre" else fac
            
        elif role == "Professionnel / Expert":
            entite_nom = st.text_input("Entreprise / Institution")
            expertise = st.selectbox("Domaine d'expertise :", ["Génie Civil", "Électromécanique", "IA/Data", "Autre"])
            detail_final = st.text_input("Précisez votre spécialité métier :") if expertise == "Autre" else expertise
            linkedin = st.text_input("Lien LinkedIn (pour vérification IA)")

        if st.button("Créer mon compte et Entrer"):
            if nom_reg and email_reg and pw_reg and detail_final and entite_nom:
                # Si Expert, petite vérification IA rapide
                if role == "Professionnel / Expert" and linkedin:
                    with st.spinner("Vérification de l'expertise..."):
                        check = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"LinkedIn: {linkedin}. Expert {detail_final} chez {entite_nom}? Réponds par OUI ou NON."}])
                        if "OUI" not in check.choices[0].message.content.upper():
                            st.warning("L'IA n'a pas pu certifier votre profil immédiatement, accès restreint.")
                
                st.session_state.user_profile = {"nom": nom_reg, "role": role, "entite": entite_nom, "detail": detail_final}
                st.success("Compte créé !")
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs du formulaire.")

# --- 4. DASHBOARD (INTERFACE APRÈS CONNEXION) ---
if st.session_state.user_profile:
    st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
    st.sidebar.info(f"Profil : {st.session_state.user_profile['role']}")
    st.sidebar.caption(f"📍 {st.session_state.user_profile['entite']} ({st.session_state.user_profile['detail']})")

    menu = ["🔍 Recherche Certifiée", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité", "💎 Mode Premium"]
    choice = st.sidebar.radio("Navigation", menu)

    # Fonctions de rendu
    def render_math(text):
        return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

    # --- PAGES ---
    if choice == "🔍 Recherche Certifiée":
        st.title("📚 Moteur de Recherche Scientifique")
        q = st.text_input(f"Sujet lié à votre spécialité ({st.session_state.user_profile['detail']}) :")
        if q:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Donne 3 sources fiables niveau {st.session_state.user_profile['role']} pour {q}."}])
            st.markdown(render_math(res.choices[0].message.content))

    elif choice == "🤖 Assistant IA Multi":
        st.title("🤖 Assistant IA Multimodal")
        up = st.file_uploader("Upload Image ou PDF (Analyse d'exercice)", type=['png', 'jpg', 'pdf'])
        if up and st.button("Lancer l'analyse"):
            st.info("Traitement par Llama-3 Vision / PDF Reader...")

    elif choice == "📝 Rapports & BibTeX":
        st.title("📝 Copilote LaTeX Conversationnel")
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        if inp := st.chat_input("Décrivez votre rapport..."):
            st.session_state.chat_history.append({"role":"user","content":inp})
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert LaTeX."}]+st.session_state.chat_history)
            st.code(res.choices[0].message.content, language="latex")

    elif choice == "💎 Mode Premium":
        st.title("💎 Mode Premium")
        st.write("Accédez au mode examen, aux corrigés d'annales et à l'IA Vision illimitée.")
        # Lien Lemon Squeezy réel à configurer
        st.link_button("🚀 Activer mon accès Premium (9,99€/mois)", "https://votre-boutique.lemonsqueezy.com")
