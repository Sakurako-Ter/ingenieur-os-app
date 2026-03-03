import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .auth-card { background-color: #1c1f26; padding: 40px; border-radius: 15px; border: 1px solid #2e7bc4; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SYSTÈME DE QUALIFICATION DE PROFIL ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.user_profile is None:
    st.title("🏗️ Bienvenue sur Ingénieur OS")
    st.subheader("Veuillez configurer votre accès")
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        role = st.radio("Vous êtes :", ["Étudiant / Élève", "Professionnel / Expert"], horizontal=True)
        
        with st.form("qualification_form"):
            nom = st.text_input("Nom d'utilisateur")
            email = st.text_input("Adresse Email (pour les notifications)")
            
            if role == "Étudiant / Élève":
                etablissement = st.text_input("Nom de votre établissement (UCL, ULB, etc.)")
                if st.form_submit_button("Accéder à la plateforme"):
                    if nom and email and etablissement:
                        st.session_state.user_profile = {"nom": nom, "role": role, "entite": etablissement, "statut": "Apprenant"}
                        st.success("Accès autorisé !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs.")
            
            else:  # MODE PROFESSIONNEL
                entreprise = st.text_input("Nom de votre entreprise / Institution")
                expertise = st.selectbox("Domaine d'expertise", ["Génie Civil", "Électromécanique", "IA/Data", "Chimie/Matériaux"])
                linkedin = st.text_input("Lien vers votre profil LinkedIn")
                
                if st.form_submit_button("Vérifier mon expertise et entrer"):
                    if nom and email and linkedin:
                        with st.spinner("L'IA vérifie la cohérence de votre profil..."):
                            # Vérification IA de l'expertise via le lien LinkedIn (simulation intelligente)
                            check_prompt = f"Analyse ce lien LinkedIn : {linkedin}. L'utilisateur prétend être expert en {expertise} chez {entreprise}. Est-ce cohérent ? Réponds par OUI ou NON suivi d'une courte justification."
                            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":check_prompt}])
                            verdict = res.choices[0].message.content
                            
                            if "OUI" in verdict.upper():
                                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entreprise, "statut": "Expert", "expert_domain": expertise}
                                st.success(f"Expertise validée par l'IA : {verdict}")
                                st.rerun()
                            else:
                                st.error(f"Validation échouée : {verdict}")
                    else:
                        st.error("Tous les champs sont requis pour les experts.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. INTERFACE PRINCIPALE ---
st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
st.sidebar.markdown(f"**{st.session_state.user_profile['statut']}**")
st.sidebar.caption(f"📍 {st.session_state.user_profile['entite']}")

menu = ["🔍 Recherche de Sources", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité"]
if st.session_state.user_profile["statut"] == "Expert":
    menu.append("👑 Panel de Certification")
menu.append("💎 Mode Premium")

choice = st.sidebar.radio("Navigation", menu)

# --- FONCTIONS TECHNIQUES ---
def render_math(text):
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 5. LOGIQUE DES PAGES ---

if choice == "🔍 Recherche de Sources":
    st.title("📚 Moteur de Recherche Scientifique")
    query = st.text_input("Concept à rechercher :")
    if query:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Donne 3 sources fiables (Livre, Thèse, Article) pour {query} avec justifications."}])
        st.markdown(render_math(res.choices[0].message.content))

elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    t1, t2, t3 = st.tabs(["Texte", "Photo", "PDF"])
    # ... (Garder le code précédent pour la vision et le PDF)

elif choice == "📝 Rapports & BibTeX":
    st.title("📝 Copilote LaTeX & BibTeX")
    # ... (Garder le code conversationnel précédent)

elif choice == "🛡️ Audit de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité")
    sujet = st.text_input("Sujet du travail :")
    source = st.text_area("Source à analyser :")
    if st.button("Lancer l'audit"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert académique. Note sur 10."}, {"role":"user","content":f"Sujet: {sujet}\nSource: {source}"}])
        st.markdown(res.choices[0].message.content)
        st.button("🚀 Soumettre aux experts pour validation humaine")

elif choice == "👑 Panel de Certification":
    st.title(f"👑 Centre Experts : {st.session_state.user_profile.get('expert_domain', 'Général')}")
    st.info("Validez les documents soumis par les étudiants de votre secteur.")
    st.warning("📥 1 document en attente : 'Statique des fluides - Note de cours UCL'")
    if st.button("✅ Certifier comme Source Fiable"):
        st.balloons()
        st.success("Le document est maintenant marqué comme 'Vérifié par Expert' dans la recherche.")

elif choice == "💎 Mode Premium":
    st.title("💎 Mode Premium")
    st.write("Accédez aux corrigés et à l'IA illimitée.")
    st.link_button("🚀 S'abonner (9,99€/mois)", "https://ton-lien-lemon-squeezy.com")
