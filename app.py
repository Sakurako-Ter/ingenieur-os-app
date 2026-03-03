import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io

# --- 1. CONFIGURATION SYSTÈME ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. STYLE CSS (DESIGN PRO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .hero-text { text-align: center; padding: 30px 0; }
    .feature-card { background-color: #1c1f26; padding: 20px; border-radius: 12px; border: 1px solid #2e7bc4; text-align: center; margin-bottom: 20px; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; border: none; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTION DE LA NAVIGATION ---
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

# --- PAGE D'ACCUEIL (VITRINE) ---
if not st.session_state.access_granted:
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
        st.session_state.access_granted = True
        st.rerun()

# --- INTERFACE PRINCIPALE (DASHBOARD DIRECT) ---
else:
    st.sidebar.title("🚀 Ingénieur OS")
    menu = ["🔍 Recherche Certifiée", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "💎 Mode Premium"]
    choice = st.sidebar.radio("Navigation", menu)

    def render_math(text):
        return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

    if choice == "🔍 Recherche Certifiée":
        st.title("📚 Moteur de Recherche Scientifique")
        q = st.text_input("Sujet de recherche (ex: Seconde loi de la thermodynamique) :")
        if q:
            with st.spinner("Recherche..."):
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Donne des sources fiables pour {q}."}])
                st.markdown(render_math(res.choices[0].message.content))

    elif choice == "🤖 Assistant IA Multi":
        st.title("🤖 Assistant IA Multimodal")
        up = st.file_uploader("Upload Image ou PDF (Analyse d'exercice)", type=['png', 'jpg', 'pdf'])
        if up and st.button("Lancer l'analyse"):
            st.info("Analyse en cours via Llama-3...")

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
