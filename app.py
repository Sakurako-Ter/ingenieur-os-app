import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io

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
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FORMULAIRE D'ACCÈS ADAPTATIF ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.user_profile is None:
    st.title("🏗️ Ingénieur OS : Accès Sécurisé")
    st.subheader("Plateforme d'aide à la réussite (Secondaire & Supérieur)")
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        role = st.radio("Votre profil :", ["Élève (Secondaire)", "Étudiant (Université/Haute École)", "Professionnel / Expert"], horizontal=True)
        
        with st.form("qualification_form"):
            nom = st.text_input("Nom d'utilisateur / Pseudo")
            email = st.text_input("Adresse Email")
            
            if role == "Élève (Secondaire)":
                ecole = st.text_input("Nom de votre École (ex: Collège St-Pierre, Athénée...)")
                option = st.selectbox("Votre option :", ["Math Fortes", "Sciences", "Général", "Technique"])
                if st.form_submit_button("Accéder aux outils de réussite"):
                    if nom and email and ecole:
                        st.session_state.user_profile = {"nom": nom, "role": role, "entite": ecole, "statut": "Élève", "detail": option}
                        st.rerun()
            
            elif role == "Étudiant (Université/Haute École)":
                univ = st.text_input("Université ou École (ex: UCL, ULB, Liège, Mons...)")
                fac = st.selectbox("Faculté :", ["EPL/Polytech", "Sciences", "Architecture", "Autre"])
                if st.form_submit_button("Accéder aux ressources Univ"):
                    if nom and email and univ:
                        st.session_state.user_profile = {"nom": nom, "role": role, "entite": univ, "statut": "Étudiant", "detail": fac}
                        st.rerun()
            
            else:  # PROFESSIONNEL / EXPERT
                entreprise = st.text_input("Entreprise ou Institution")
                expertise = st.selectbox("Expertise :", ["Génie Civil", "Électromécanique", "IA/Data", "Matériaux"])
                linkedin = st.text_input("Lien LinkedIn (vérification IA)")
                if st.form_submit_button("Vérifier et entrer"):
                    if nom and linkedin:
                        with st.spinner("Vérification de l'expertise..."):
                            check = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Analyse ce LinkedIn: {linkedin}. Expert en {expertise} chez {entreprise}? Réponds par OUI ou NON."}])
                            if "OUI" in check.choices[0].message.content.upper():
                                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entreprise, "statut": "Expert", "detail": expertise}
                                st.rerun()
                            else:
                                st.error("L'IA n'a pas pu confirmer votre expertise via ce lien.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
st.sidebar.info(f"Rôle : {st.session_state.user_profile['role']}")
st.sidebar.caption(f"📍 {st.session_state.user_profile['entite']}")

menu = ["🔍 Recherche de Sources", "🤖 Assistant IA", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité"]
if st.session_state.user_profile["statut"] == "Expert":
    menu.append("👑 Panel de Certification")
menu.append("💎 Mode Premium")
choice = st.sidebar.radio("Navigation", menu)

# --- 5. PAGES ---

def render_math(text):
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

if choice == "🔍 Recherche de Sources":
    st.title("📚 Moteur de Recherche")
    niveau = "Secondaire" if st.session_state.user_profile["statut"] == "Élève" else "Universitaire"
    query = st.text_input(f"Sujet ({niveau}) :")
    if query:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":f"Donne des sources fiables niveau {niveau}."}, {"role":"user","content":query}])
        st.markdown(render_math(res.choices[0].message.content))

elif choice == "🤖 Assistant IA":
    st.title("🤖 Assistant IA Multi-supports")
    # Inclusion des fonctions Photo/PDF/Texte ici...
    # L'IA peut adapter ses explications selon st.session_state.user_profile["statut"]

elif choice == "📝 Rapports & BibTeX":
    st.title("📝 Aide à la Rédaction")
    # Copilote LaTeX conversationnel ici...

elif choice == "🛡️ Audit de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité")
    source = st.text_area("Lien ou texte à vérifier :")
    if st.button("Lancer l'audit"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Vérifie la fiabilité de: {source}"}])
        st.markdown(res.choices[0].message.content)
        st.button("🚀 Soumettre aux experts pour validation")

elif choice == "👑 Panel de Certification":
    st.title(f"👑 Validation Expert : {st.session_state.user_profile['detail']}")
    st.warning("📄 1 document soumis par un étudiant en attente de validation.")
    if st.button("✅ Certifier la source"):
        st.balloons()
        st.success("Document publié dans la base de données certifiée.")

elif choice == "💎 Mode Premium":
    st.title("💎 Mode Premium")
    prix = "4.99€" if st.session_state.user_profile["statut"] == "Élève" else "9.99€"
    st.write(f"Tarif adapté à votre profil : **{prix}/mois**")
    st.link_button("S'abonner via Lemon Squeezy", "https://ton-lien-ici.com")
