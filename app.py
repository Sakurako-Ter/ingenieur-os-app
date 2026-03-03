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

# A. PAGE D'ACCUEIL VITRINE
if st.session_state.user_profile is None and st.session_state.page == "home":
    st.markdown('<div class="hero-text"><h1>🏗️ INGÉNIEUR OS</h1><h3>L\'écosystème de réussite certifié pour ingénieurs.</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card">🔍 <b>Recherche</b><p>Sources certifiées</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card">🤖 <b>IA Multimodale</b><p>Analyse Photo & PDF</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card">📝 <b>LaTeX</b><p>Copilote de rapports pro</p></div>', unsafe_allow_html=True)
    
    if st.button("🚀 ACCÉDER À LA PLATEFORME"):
        st.session_state.page = "config_profile"
        st.rerun()

# B. PAGE DE CONFIGURATION INITIALE DU PROFIL (SANS AUTH)
elif st.session_state.user_profile is None and st.session_state.page == "config_profile":
    st.title("🏗️ Configurez votre Profil")
    
    with st.form("main_reg_form"):
        role = st.radio("Votre profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], horizontal=True)
        nom = st.text_input("Nom / Pseudo")
        entite = st.text_input("École / Université / Entreprise")
        
        # Gestion dynamique du détail
        st.write("---")
        expertise_list = ["Math Fortes", "Sciences", "Polytech", "Génie Civil", "IA/Data", "Autre"]
        detail_selection = st.selectbox("Domaine / Faculté / Option :", expertise_list)
        
        detail_precision = ""
        if detail_selection == "Autre":
            detail_precision = st.text_input("Précisez votre spécialité exacte :")
        
        link = st.text_input("Lien LinkedIn (Obligatoire pour les Experts)")
        
        submitted = st.form_submit_button("Valider et Entrer")
        
        if submitted:
            final_detail = detail_precision if detail_selection == "Autre" else detail_selection
            if role == "Professionnel / Expert":
                verdict = verify_expert(link, final_detail, entite)
                if "OUI" in verdict.upper():
                    st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite, "detail": final_detail, "link": link}
                    st.rerun()
                else:
                    st.error(f"Validation échouée : {verdict}")
            elif nom and entite and final_detail:
                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite, "detail": final_detail, "link": ""}
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs.")

# C. INTERFACE PRINCIPALE (DASHBOARD)
elif st.session_state.user_profile:
    st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
    st.sidebar.info(f"Profil : {st.session_state.user_profile['role']}")
    st.sidebar.caption(f"📍 {st.session_state.user_profile['entite']} ({st.session_state.user_profile['detail']})")
    
    menu = ["🔍 Recherche Certifiée", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "⚙️ Modifier mon Profil", "💎 Premium"]
    choice = st.sidebar.radio("Navigation", menu)

    def render_math(text):
        return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

    # --- PAGE MODIFIER PROFIL ---
    if choice == "⚙️ Modifier mon Profil":
        st.title("⚙️ Paramètres du Profil")
        with st.form("update_form"):
            new_role = st.radio("Changer de profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], 
                                index=["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"].index(st.session_state.user_profile['role']))
            new_entite = st.text_input("École / Univ / Entreprise", value=st.session_state.user_profile['entite'])
            new_detail = st.text_input("Spécialité / Option", value=st.session_state.user_profile['detail'])
            new_link = st.text_input("Lien LinkedIn (si Expert)", value=st.session_state.user_profile['link'])
            
            if st.form_submit_button("Sauvegarder les modifications"):
                if new_role == "Professionnel / Expert":
                    verdict = verify_expert(new_link, new_detail, new_entite)
                    if "OUI" in verdict.upper():
                        st.session_state.user_profile.update({"role": new_role, "entite": new_entite, "detail": new_detail, "link": new_link})
                        st.success("Profil Expert validé !")
                    else:
                        st.error(f"Échec de validation : {verdict}")
                else:
                    st.session_state.user_profile.update({"role": new_role, "entite": new_entite, "detail": new_detail})
                    st.success("Profil mis à jour !")

    elif choice == "🔍 Recherche Certifiée":
        st.title("📚 Moteur de Recherche Scientifique")
        q = st.text_input("Sujet :")
        if q:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Donne des sources fiables pour {q}."}])
            st.markdown(render_math(res.choices[0].message.content))

    elif choice == "🤖 Assistant IA Multi":
        st.title("🤖 Assistant IA Multimodal")
        up = st.file_uploader("Upload Image ou PDF", type=['png', 'jpg', 'pdf'])
        if up: st.info("Fichier chargé. Utilisez l'IA pour l'analyser.")

    elif choice == "💎 Premium":
        st.title("💎 Mode Premium")
        st.link_button("🚀 S'abonner (9,99€/mois)", "https://votre-boutique.lemonsqueezy.com")
