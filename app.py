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

# --- 2. STYLE CSS (DESIGN ÉPURÉ) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .auth-card { 
        background-color: #1c1f26; 
        padding: 30px; 
        border-radius: 15px; 
        border: 1px solid #2e7bc4;
        margin-top: -20px;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #1e5ba0; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SYSTÈME D'ACCÈS DYNAMIQUE ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.user_profile is None:
    st.title("🏗️ Ingénieur OS")
    
    # Ouverture de la boîte de formulaire sans espace vide
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.subheader("Accès Certifié & Aide à la Réussite")
    
    role = st.radio("Choisissez votre profil :", ["Élève (Secondaire)", "Étudiant (Université)", "Professionnel / Expert"], horizontal=True)
    
    # Champs de base
    nom = st.text_input("Nom d'utilisateur / Pseudo")
    email = st.text_input("Adresse Email")

    detail_final = ""
    entite_nom = ""
    linkedin_url = ""

    # --- LOGIQUE DYNAMIQUE SELON LE RÔLE ---
    if role == "Élève (Secondaire)":
        entite_nom = st.text_input("Nom de votre École (ex: Collège St-Pierre)")
        option = st.selectbox("Votre option :", ["Math Fortes", "Sciences", "Technique", "Autre"])
        if option == "Autre":
            detail_final = st.text_input("Précisez votre option exacte :")
        else:
            detail_final = option

    elif role == "Étudiant (Université)":
        entite_nom = st.text_input("Université (ex: UCL, ULB, ULiège, UMons...)")
        fac = st.selectbox("Faculté :", ["EPL/Polytech", "Sciences", "Architecture", "Autre"])
        if fac == "Autre":
            detail_final = st.text_input("Précisez votre Faculté / Filière précise :")
        else:
            detail_final = fac

    elif role == "Professionnel / Expert":
        entite_nom = st.text_input("Entreprise ou Institution")
        expertise = st.selectbox("Domaine d'expertise :", ["Génie Civil", "Électromécanique", "IA/Data", "Matériaux", "Autre"])
        if expertise == "Autre":
            detail_final = st.text_input("Précisez votre spécialité métier exacte :")
        else:
            detail_final = expertise
        linkedin_url = st.text_input("Lien vers votre profil LinkedIn (Vérification IA)")

    # --- BOUTON DE VALIDATION ---
    if st.button("Valider et Entrer"):
        if nom and email and entite_nom and detail_final:
            if role == "Professionnel / Expert":
                if not linkedin_url:
                    st.error("Le lien LinkedIn est requis pour les experts.")
                else:
                    with st.spinner(f"Vérification de l'expertise en {detail_final}..."):
                        try:
                            check = client.chat.completions.create(
                                model="llama-3.3-70b-versatile", 
                                messages=[{"role":"user","content":f"Analyse ce LinkedIn: {linkedin_url}. Expert en {detail_final} chez {entite_nom}? Réponds par OUI ou NON + raison."}]
                            )
                            verdict = check.choices[0].message.content
                            if "OUI" in verdict.upper():
                                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite_nom, "statut": "Expert", "detail": detail_final}
                                st.rerun()
                            else:
                                st.error(f"Validation échouée : {verdict}")
                        except Exception as e:
                            st.error(f"Erreur IA : {e}")
            else:
                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entite_nom, "statut": role, "detail": detail_final}
                st.rerun()
        else:
            st.error("Veuillez remplir tous les champs.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION (DASHBOARD) ---
st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
st.sidebar.info(f"Profil : {st.session_state.user_profile['role']}")
st.sidebar.caption(f"📍 {st.session_state.user_profile['entite']} ({st.session_state.user_profile['detail']})")

menu = ["🔍 Recherche de Sources", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité"]
if st.session_state.user_profile["statut"] == "Expert":
    menu.append("👑 Panel de Certification")
menu.append("💎 Mode Premium")
choice = st.sidebar.radio("Navigation", menu)

def render_math(text):
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 5. LOGIQUE DES PAGES ---

if choice == "🔍 Recherche de Sources":
    st.title("📚 Moteur de Recherche de Sources")
    q = st.text_input(f"Sujet lié à {st.session_state.user_profile['detail']} :")
    if q:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Sources fiables pour {q}."}])
        st.markdown(render_math(res.choices[0].message.content))

elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multimodal")
    t1, t2, t3 = st.tabs(["Texte", "Photo d'exercice", "Document PDF"])
    with t2:
        img_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        if img_file and st.button("Analyser Image"):
            b64 = base64.b64encode(img_file.getvalue()).decode('utf-8')
            res = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role":"user","content":[{"type":"text","text":"Explique en LaTeX."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}])
            st.markdown(render_math(res.choices[0].message.content))
    with t3:
        pdf_file = st.file_uploader("Upload PDF", type=['pdf'])
        if pdf_file and st.button("Lire PDF"):
            reader = PyPDF2.PdfReader(pdf_file)
            content = "".join([p.extract_text() for p in reader.pages[:3]])
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Analyse ce PDF: {content[:5000]}"}])
            st.markdown(render_math(res.choices[0].message.content))

elif choice == "📝 Rapports & BibTeX":
    st.title("📝 Copilote LaTeX Conversationnel")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"]) if msg["role"]=="user" else st.code(msg["content"], language="latex")
    if inp := st.chat_input("Décrivez votre rapport..."):
        st.session_state.chat_history.append({"role":"user","content":inp})
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Expert LaTeX. Donne UNIQUEMENT le code."}]+st.session_state.chat_history)
        st.session_state.chat_history.append({"role":"assistant","content":res.choices[0].message.content})
        st.rerun()

elif choice == "🛡️ Audit de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité")
    src = st.text_area("Source à vérifier (Lien ou Texte) :")
    if st.button("Lancer l'audit"):
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Analyse la fiabilité de : {src}"}])
        st.markdown(res.choices[0].message.content)

elif choice == "👑 Panel de Certification":
    st.title(f"👑 Validation Expert : {st.session_state.user_profile['detail']}")
    st.warning("📄 1 document en attente de certification.")
    if st.button("✅ Certifier la source"):
        st.balloons()
        st.success("Source validée et publiée.")

elif choice == "💎 Mode Premium":
    st.title("💎 Mode Premium")
    st.link_button("🚀 S'abonner (9,99€ / mois)", "https://votre-boutique.lemonsqueezy.com")
