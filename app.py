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
    st.error("⚠️ Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. STYLE CSS (SUPPRESSION DES BOITES ET ESPACES) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    /* Supprime les marges inutiles en haut */
    .block-container { padding-top: 1rem; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SYSTÈME D'ACCÈS DIRECT ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.user_profile is None:
    st.title("🏗️ Ingénieur OS")
    st.subheader("Accès Certifié & Aide à la Réussite")
    
    role = st.radio("Choisissez votre profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], horizontal=True)
    
    # Formulaire de saisie directe
    nom = st.text_input("Nom d'utilisateur / Pseudo")
    email = st.text_input("Adresse Email")

    detail_final = ""
    entite_nom = ""

    if role == "Élève (Secondaire)":
        entite_nom = st.text_input("Nom de votre École (ex: Collège St-Pierre)")
        option = st.selectbox("Votre option :", ["Math Fortes", "Sciences", "Technique", "Autre"])
        detail_final = st.text_input("Précisez votre option exacte :") if option == "Autre" else option

    elif role == "Étudiant (Université)":
        entite_nom = st.text_input("Université (ex: UCL, ULB, ULiège, UMons...)")
        fac = st.selectbox("Faculté :", ["EPL/Polytech", "Sciences", "Architecture", "Autre"])
        detail_final = st.text_input("Précisez votre Faculté / Filière :") if fac == "Autre" else fac

    elif role == "Professionnel / Expert":
        entite_nom = st.text_input("Entreprise ou Institution")
        expertise = st.selectbox("Domaine d'expertise :", ["Génie Civil", "Électromécanique", "IA/Data", "Matériaux", "Autre"])
        detail_final = st.text_input("Précisez votre spécialité métier :") if expertise == "Autre" else expertise
        linkedin = st.text_input("Lien LinkedIn (Vérification IA)")

    if st.button("Valider et Entrer"):
        if nom and email and entite_nom and detail_final:
            # Vérification IA pour les Experts
            if role == "Professionnel / Expert":
                with st.spinner("Vérification LinkedIn..."):
                    check = client.chat.completions.create(
                        model="llama-3.3-70b-versatile", 
                        messages=[{"role":"user","content":f"Analyse ce LinkedIn: {linkedin}. Expert en {detail_final} chez {entite_nom}? Réponds par OUI ou NON."}]
                    )
                    if "OUI" in check.choices[0].message.content.upper():
                        st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite_nom, "detail": detail_final}
                        st.rerun()
                    else:
                        st.error("L'IA n'a pas pu confirmer votre expertise.")
            else:
                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite_nom, "detail": detail_final}
                st.rerun()
        else:
            st.error("Veuillez remplir tous les champs.")
    st.stop()

# --- 4. NAVIGATION (DASHBOARD) ---
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

elif choice == "💎 Mode Premium":
    st.title("💎 Mode Premium")
    st.link_button("🚀 S'abonner (9,99€ / mois)", "https://votre-boutique.lemonsqueezy.com")
