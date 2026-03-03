import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
from PIL import Image

# --- 1. CONFIGURATION SYSTÈME (CORRIGÉ) ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ GROQ_API_KEY manquante dans les Secrets Streamlit.")

# --- 2. STYLE CSS (DESIGN AVANCÉ) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .hero-text { text-align: center; padding: 50px 0; }
    .feature-card { 
        background-color: #1c1f26; padding: 25px; border-radius: 15px; 
        border: 1px solid #2e7bc4; text-align: center; height: 100%;
    }
    .stat-box { font-size: 25px; font-weight: bold; color: #2e7bc4; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE D'AFFICHAGE ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if "show_register" not in st.session_state:
    st.session_state.show_register = False

# --- PAGE D'ACCUEIL (AVANT CONNEXION) ---
if st.session_state.user_profile is None and not st.session_state.show_register:
    # HERO SECTION
    st.markdown('<div class="hero-text"><h1>🏗️ INGÉNIEUR OS</h1><h3>La plateforme de certification et d\'aide à la réussite pour les futurs Ingénieurs Civils.</h3></div>', unsafe_allow_html=True)
    
    # STATISTIQUES
    col1, col2, col3 = st.columns(3)
    col1.markdown('<div style="text-align:center"><p class="stat-box">500+</p><p>Annales d\'examens</p></div>', unsafe_allow_html=True)
    col2.markdown('<div style="text-align:center"><p class="stat-box">IA Vision</p><p>Analyse de schémas</p></div>', unsafe_allow_html=True)
    col3.markdown('<div style="text-align:center"><p class="stat-box">Certifié</p><p>Par des experts métiers</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # FONCTIONNALITÉS
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="feature-card">🧪 <b>Moteur de Recherche</b><p>Trouvez les sources académiques les plus fiables (UCL, ULB, Liège...).</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-card">🤖 <b>Assistant Multimodal</b><p>L\'IA lit vos PDF et vos photos d\'exercices de physique/maths.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="feature-card">📝 <b>Copilote LaTeX</b><p>Générez vos rapports de labo et mémoires en mode conversationnel.</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # BOUTON D'ACCÈS
    if st.button("🚀 ACCÉDER À LA PLATEFORME (GRATUIT)"):
        st.session_state.show_register = True
        st.rerun()

# --- FORMULAIRE D'INSCRIPTION (DYNAMIQUE) ---
elif st.session_state.user_profile is None and st.session_state.show_register:
    st.title("🔑 Création de votre profil")
    role = st.radio("Choisissez votre profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], horizontal=True)
    
    nom = st.text_input("Nom d'utilisateur / Pseudo")
    email = st.text_input("Adresse Email")
    detail_final = ""
    entite_nom = ""

    if role == "Élève (Secondaire)":
        entite_nom = st.text_input("Nom de votre École")
        option = st.selectbox("Option :", ["Math Fortes", "Sciences", "Autre"])
        detail_final = st.text_input("Précisez l'option :") if option == "Autre" else option

    elif role == "Étudiant (Université)":
        entite_nom = st.text_input("Université (ex: UCL, ULB...)")
        fac = st.selectbox("Faculté :", ["Polytech", "Sciences", "Autre"])
        detail_final = st.text_input("Précisez la Faculté :") if fac == "Autre" else fac

    elif role == "Professionnel / Expert":
        entite_nom = st.text_input("Entreprise / Institution")
        expertise = st.selectbox("Expertise :", ["Génie Civil", "Électromécanique", "Autre"])
        detail_final = st.text_input("Précisez votre spécialité :") if expertise == "Autre" else expertise
        linkedin = st.text_input("Lien LinkedIn (Vérification IA)")

    if st.button("Valider et Entrer"):
        if nom and email and entite_nom and detail_final:
            st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite_nom, "detail": detail_final}
            st.rerun()
        else:
            st.error("Veuillez remplir tous les champs.")
            
    if st.button("⬅️ Retour à l'accueil"):
        st.session_state.show_register = False
        st.rerun()

# --- INTERFACE PRINCIPALE (APRÈS CONNEXION) ---
else:
    st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
    st.sidebar.write(f"📍 {st.session_state.user_profile['entite']}")
    
    menu = ["🔍 Recherche", "🤖 Assistant IA", "📝 Rapports", "🛡️ Audit", "💎 Premium"]
    choice = st.sidebar.radio("Navigation", menu)

    # ... (Garder ici ton code précédent pour chaque onglet)
    if choice == "💎 Premium":
        st.title("💎 Mode Premium")
        st.link_button("S'abonner (9.99€/mois)", "https://votre-boutique.lemonsqueezy.com")
