import streamlit as st
import pandas as pd
from groq import Groq
import base64
from PIL import Image
import io
import PyPDF2

# 1. INITIALISATION DU CLIENT IA
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Clé API manquante ou mal configurée dans les Secrets Streamlit.")

# Configuration de la page
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

# Style CSS pour un look pro
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextArea textarea { border: 2px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Ingénieur OS : La Plateforme Révolutionnaire Bac 1")
st.caption("Le cerveau numérique pour Polytech (UCL, ULB, ULiège, UMons...)")

# 2. MENU LATÉRAL (NAVIGATION)
menu = ["🔍 Recherche Annales (Arana)", "🤖 Assistant IA (Texte, Photo & PDF)", "📝 Aide Rapports & Mémoires", "💳 Version Premium"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- FONCTION DE NETTOYAGE LATEX POUR AFFICHAGE PROPRE ---
def clean_latex(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- PAGE 1 : RECHERCHE ANNALES (STYLE ARANA) ---
if choice == "🔍 Recherche Annales (Arana)":
    st.subheader("Moteur de Recherche Sémantique d'Examens")
    try:
        df = pd.read_csv("data/examens.csv")
        col1, col2 = st.columns(2)
        with col1:
            univ_filter = st.multiselect("Filtrer par Université :", options=df["universite"].unique())
        with col2:
            search_query = st.text_input("Chercher un concept (ex: Moment d'inertie, Matrices...)")

        filtered_df = df
        if univ_filter:
            filtered_df = filtered_df[filtered_df["universite"].isin(univ_filter)]
        if search_query:
            filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        st.write(f"### {len(filtered_df)} Ressources trouvées")
        st.dataframe(filtered_df, use_container_width=True)
    except:
        st.info("ℹ️ La base de données 'data/examens.csv' est vide. Ajoutez des annales sur GitHub pour activer la recherche.")

# --- PAGE 2 : ASSISTANT IA MULTIMODAL (TEXTE, PHOTO, PDF) ---
elif choice == "🤖 Assistant IA (Texte, Photo & PDF)":
    st.subheader("Assistant IA Multi-supports")
    mode = st.radio("Comment veux-tu étudier ?", ["Énoncé Texte", "Photo d'exercice / Schéma", "Document PDF (Syllabus/Examen)"])
    
    # --- OPTION PDF ---
    if mode == "Document PDF (Syllabus/Examen)":
        pdf_file = st.file_uploader("Upload ton PDF :", type=["pdf"])
        query = st.text_input("Que veux-tu savoir ?", "Explique les concepts clés et les méthodes de résolution de ce document.")
        if pdf_file and st.button("Analyser le PDF"):
            with st.spinner("Lecture et analyse du PDF..."):
                try:
                    reader = PyPDF2.PdfReader(pdf_file)
                    pdf_text = ""
                    # On limite à 5 pages pour la version gratuite/performance
                    for i in range(min(5, len(reader.pages))):
                        pdf_text += reader.pages[i].extract_text()
                    
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Tu es un tuteur expert en ingénierie. Analyse le texte suivant et réponds en LaTeX rigoureux."},
                            {"role": "user", "content": f"Texte du PDF: {pdf_text[:8000]}\n\nQuestion: {query}"}
                        ]
                    )
                    st.markdown("### 📘 Analyse du PDF :")
                    st.markdown(clean_latex(completion.choices.message.content))
                except Exception as e:
                    st.error(f"Erreur d'analyse PDF : {e}")

    # --- OPTION PHOTO ---
    elif mode == "Photo d'exercice / Schéma":
        img_file = st.file_uploader("Upload une photo :", type=["jpg", "jpeg", "png"])
        if img_file:
            st.image(img_file, width=300)
            if st.button("Analyser l'image"):
                with st.spinner("L'IA examine le schéma..."):
                    try:
                        base64_img = base64.b64encode(img_file.getvalue()).decode('utf-8')
                        res = client.chat.completions.create(
                            model="llama-3.2-11b-vision-preview",
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyse cet exercice d'ingénieur. Explique la méthode en LaTeX."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                                ]
                            }]
                        )
                        st.markdown("### 📘 Analyse de la photo :")
                        st.markdown(clean_latex(res.choices.message.content))
                    except Exception as e:
                        st.error(f"Erreur Vision : {e}")

    # --- OPTION TEXTE ---
    else:
        text_input = st.text_area("Colle l'énoncé ici :", height=150)
        if st.button("Analyser le texte"):
            with st.spinner("Réflexion en cours..."):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Tu es un tuteur expert en ingénierie. Réponds en LaTeX rigoureux."},
                            {"role": "user", "content": text_input}
                        ]
                    )
                    st.markdown("### 📘 Méthode de résolution :")
                    st.markdown(clean_latex(res.choices.message.content))
                except Exception as e:
                    st.error(f"Erreur : {e}")

# --- PAGE 3 : RAPPORTS LATEX (CONVERSATIONNEL) ---
elif choice == "📝 Rapports LaTeX":
    st.title("📝 Copilote LaTeX Conversationnel")
    st.info("Explique ton projet ci-dessous. Tu peux demander des modifications au fur et à mesure (ex: 'Ajoute une table des matières').")

    # Initialisation de la mémoire de l'assistant
    if "latex_chat_history" not in st.session_state:
        st.session_state.latex_chat_history = []

    # Affichage des échanges précédents
    for msg in st.session_state.latex_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de dialogue
    if user_input := st.chat_input("Décris ton rapport ou demande une modification..."):
        st.session_state.latex_chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Rédaction du code LaTeX..."):
                try:
                    # Envoi de l'historique complet pour garder le contexte
                    messages = [
                        {"role": "system", "content": "Tu es un expert LaTeX. Génère UNIQUEMENT le code complet. Pas de bla-bla inutile."}
                    ] + st.session_state.latex_chat_history
                    
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages
                    )
                    
                    full_code = res.choices.message.content
                    st.session_state.latex_chat_history.append({"role": "assistant", "content": full_code})
                    
                    st.markdown("### ✅ Ton Code LaTeX mis à jour :")
                    st.code(full_code, language="latex")
                    
                    # Bouton de téléchargement dynamique
                    st.download_button("📥 Télécharger le fichier .tex", full_code, file_name="mon_rapport.tex")
                    
                except Exception as e:
                    st.error(f"Erreur : {e}")


# --- PAGE 4 : PREMIUM ---
elif choice == "💳 Version Premium":
    st.subheader("Passe à l'Ingénierie Supérieure")
    st.write("""
    **L'abonnement Premium débloque :**
    - ✅ Accès illimité aux PDF (plus de 5 pages)
    - ✅ Corrigés détaillés des examens UCL/ULB/Liège
    - ✅ IA Vision prioritaire et plus rapide
    """)
    st.link_button("S'abonner (9,99€ / mois)", "https://www.lemonsqueezy.com")
