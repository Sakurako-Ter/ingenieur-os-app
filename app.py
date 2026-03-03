import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io
from PIL import Image

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
    .auth-card { background-color: #1c1f26; padding: 30px; border-radius: 15px; border: 1px solid #2e7bc4; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #2e7bc4; color: white; transition: 0.3s; }
    .stButton>button:hover { background-color: #1e5ba0; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SYSTÈME D'ACCÈS ADAPTATIF ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if st.session_state.user_profile is None:
    st.title("🏗️ Ingénieur OS : Accès Sécurisé")
    st.subheader("Plateforme de certification et d'aide à la réussite")
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        role = st.radio("Choisissez votre profil :", ["Élève (Secondaire)", "Étudiant (Université/Haute École)", "Professionnel / Expert"], horizontal=True)
        
        with st.form("qualification_form"):
            nom = st.text_input("Nom d'utilisateur / Pseudo")
            email = st.text_input("Adresse Email (Contact)")
            
            # --- CAS ÉLÈVE ---
            if role == "Élève (Secondaire)":
                ecole = st.text_input("Nom de votre École (ex: Collège St-Pierre, Athénée...)")
                option = st.selectbox("Votre option :", ["Math Fortes", "Sciences", "Général", "Technique", "Autre"])
                precision = st.text_input("Précisez votre option (si Autre) :") if option == "Autre" else ""
                
                if st.form_submit_button("Accéder aux outils"):
                    if nom and email and ecole:
                        st.session_state.user_profile = {"nom": nom, "role": role, "entite": ecole, "statut": "Élève", "detail": precision if option == "Autre" else option}
                        st.rerun()

            # --- CAS ÉTUDIANT ---
            elif role == "Étudiant (Université/Haute École)":
                univ = st.text_input("Université ou École (ex: UCL, ULB, Liège, Mons...)")
                fac = st.selectbox("Faculté :", ["EPL/Polytech", "Sciences", "Architecture", "Autre"])
                precision_fac = st.text_input("Précisez votre Faculté/Filière :") if fac == "Autre" else ""
                
                if st.form_submit_button("Accéder aux ressources"):
                    if nom and email and univ:
                        st.session_state.user_profile = {"nom": nom, "role": role, "entite": univ, "statut": "Étudiant", "detail": precision_fac if fac == "Autre" else fac}
                        st.rerun()

            # --- CAS PROFESSIONNEL / EXPERT ---
            else:
                entreprise = st.text_input("Entreprise ou Institution")
                expertise = st.selectbox("Domaine d'expertise :", ["Génie Civil", "Électromécanique", "IA/Data", "Matériaux", "Autre"])
                precision_exp = st.text_input("Précisez votre spécialité (ex: Géotechnique) :") if expertise == "Autre" else ""
                linkedin = st.text_input("Lien LinkedIn (Vérification IA)")
                
                if st.form_submit_button("Vérifier et entrer"):
                    final_exp = precision_exp if expertise == "Autre" else expertise
                    if nom and linkedin:
                        with st.spinner("Vérification de l'expertise via IA..."):
                            check = client.chat.completions.create(
                                model="llama-3.3-70b-versatile", 
                                messages=[{"role":"user","content":f"Analyse ce LinkedIn: {linkedin}. Est-il cohérent pour un expert en {final_exp} chez {entreprise}? Réponds par OUI ou NON + courte raison."}]
                            )
                            verdict = check.choices[0].message.content
                            if "OUI" in verdict.upper():
                                st.session_state.user_profile = {"nom": nom, "role": role, "entite": entreprise, "statut": "Expert", "detail": final_exp}
                                st.rerun()
                            else:
                                st.error(f"Vérification échouée : {verdict}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. NAVIGATION ---
st.sidebar.title(f"🚀 {st.session_state.user_profile['nom']}")
st.sidebar.info(f"Profil : {st.session_state.user_profile['role']}")
st.sidebar.caption(f"📍 {st.session_state.user_profile['entite']} - {st.session_state.user_profile['detail']}")

menu = ["🔍 Recherche de Sources", "🤖 Assistant IA Multi", "📝 Rapports & BibTeX", "🛡️ Audit de Fiabilité"]
if st.session_state.user_profile["statut"] == "Expert":
    menu.append("👑 Panel de Certification")
menu.append("💎 Mode Premium")
choice = st.sidebar.radio("Navigation", menu)

def render_math(text):
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 5. LOGIQUE DES PAGES ---

if choice == "🔍 Recherche de Sources":
    st.title("📚 Moteur de Recherche de Sources Fiables")
    query = st.text_input("Sujet de recherche :")
    if query:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Donne des sources fiables (Livre, Thèse, Article) pour {query} niveau {st.session_state.user_profile['statut']}."}])
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
    st.title(f"👑 Centre de Validation : {st.session_state.user_profile['detail']}")
    st.warning("📄 1 document en attente de certification.")
    if st.button("✅ Valider la source"):
        st.balloons()
        st.success("Document certifié et ajouté à la base de données publique.")

elif choice == "💎 Mode Premium":
    st.title("💎 Services Premium")
    st.markdown("- **IA Vision illimitée**\n- **Planning de révision dynamique**\n- **Accès aux sources certifiées**")
    st.link_button("S'abonner (9,99€ / mois)", "https://ton-lien-lemon-squeezy.com")
