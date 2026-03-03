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

# --- FONCTION DE VÉRIFICATION EXPERT ---
def verify_expert(linkedin, expertise, entreprise):
    with st.spinner("L'IA vérifie la cohérence de votre expertise..."):
        try:
            check = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role":"user","content":f"Analyse ce LinkedIn: {linkedin}. Expert en {expertise} chez {entreprise}? Réponds par OUI ou NON + courte raison."}]
            )
            return check.choices[0].message.content
        except:
            return "NON - Erreur de connexion IA"

# --- 4. LOGIQUE D'ACCÈS ---

# A. PAGE D'ACCUEIL
if st.session_state.user_profile is None and st.session_state.page == "home":
    st.markdown('<div class="hero-text"><h1>🏗️ INGÉNIEUR OS</h1><h3>L\'écosystème de réussite certifié pour ingénieurs.</h3></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="feature-card">🔍 <b>Recherche</b><p>Sources certifiées</p></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="feature-card">🤖 <b>IA Multimodale</b><p>Analyse Photo & PDF</p></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="feature-card">📝 <b>LaTeX</b><p>Copilote de rapports</p></div>', unsafe_allow_html=True)
    if st.button("🚀 ACCÉDER À LA PLATEFORME"):
        st.session_state.page = "auth"
        st.rerun()

# B. PAGE D'AUTHENTIFICATION
elif st.session_state.user_profile is None and st.session_state.page == "auth":
    st.title("🏗️ Authentification")
    tab_login, tab_reg = st.tabs(["🔐 Connexion", "📝 Créer un compte"])
    
    with tab_reg:
        with st.form("reg_form"):
            role = st.radio("Profil :", ["Élève", "Étudiant", "Expert"], horizontal=True)
            nom = st.text_input("Nom / Pseudo")
            email = st.text_input("Email")
            pw = st.text_input("Mot de passe", type="password")
            entite = st.text_input("École / Univ / Entreprise")
            detail = st.text_input("Spécialité / Faculté précise")
            link = st.text_input("Lien LinkedIn (Uniquement pour Expert)")
            
            if st.form_submit_button("Créer mon compte"):
                if role == "Expert":
                    verdict = verify_expert(link, detail, entite)
                    if "OUI" in verdict.upper():
                        st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite, "detail": detail, "email": email, "pw": pw, "link": link}
                        st.rerun()
                    else: st.error(f"Validation échouée : {verdict}")
                elif nom and email and pw:
                    st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite, "detail": detail, "email": email, "pw": pw, "link": ""}
                    st.rerun()
    # (Login simplifié pour le test)
    with tab_login:
        e_l = st.text_input("Email")
        p_l = st.text_input("Pass", type="password")
        if st.button("Entrer"): st.session_state.user_profile = {"nom": "Test", "role": "Étudiant", "entite": "UCL", "detail": "Polytech", "email": e_l, "pw": p_l} ; st.rerun()

# C. INTERFACE PRINCIPALE
elif st.session_state.user_profile:
    st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
    menu = ["🔍 Recherche", "🤖 Assistant IA", "📝 Rapports", "⚙️ Mon Profil", "💎 Premium"]
    choice = st.sidebar.radio("Navigation", menu)

    # --- PAGE CHANGEMENT DE PROFIL ---
    if choice == "⚙️ Mon Profil":
        st.title("⚙️ Paramètres du Profil")
        st.info(f"Profil actuel : **{st.session_state.user_profile['role']}** chez {st.session_state.user_profile['entite']}")
        
        with st.form("update_profile"):
            new_role = st.radio("Changer de statut :", ["Élève", "Étudiant", "Expert"], index=["Élève", "Étudiant", "Expert"].index(st.session_state.user_profile['role']))
            new_entite = st.text_input("Nouvelle École / Entreprise", value=st.session_state.user_profile['entite'])
            new_detail = st.text_input("Nouvelle Spécialité", value=st.session_state.user_profile['detail'])
            new_link = st.text_input("Lien LinkedIn (Obligatoire si Expert)", value=st.session_state.user_profile['link'])
            
            if st.form_submit_button("Enregistrer les modifications"):
                # Si le nouveau rôle est Expert, on relance la vérification IA
                if new_role == "Expert":
                    verdict = verify_expert(new_link, new_detail, new_entite)
                    if "OUI" in verdict.upper():
                        st.session_state.user_profile.update({"role": new_role, "entite": new_entite, "detail": new_detail, "link": new_link})
                        st.success("Profil Expert certifié et mis à jour !")
                    else:
                        st.error(f"Échec de la certification Expert : {verdict}")
                else:
                    st.session_state.user_profile.update({"role": new_role, "entite": new_entite, "detail": new_detail})
                    st.success("Profil mis à jour !")

    elif choice == "🔍 Recherche":
        st.title("🔍 Sources Certifiées")
        q = st.text_input("Sujet :")
        if q:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Sources pour {q}"}])
            st.write(res.choices[0].message.content)

    elif choice == "💎 Premium":
        st.title("💎 Premium")
        st.link_button("S'abonner (9.99€)", "https://votre-boutique.lemonsqueezy.com")
