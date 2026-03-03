import streamlit as st
import pandas as pd
from groq import Groq
import base64

# 1. INITIALISATION DU CLIENT IA
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Clé API manquante dans les Secrets Streamlit.")

# Configuration de la page
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

# Style CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; }
    .reportview-container { background: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Ingénieur OS : La Plateforme Révolutionnaire Bac 1")
st.caption("Le cerveau numérique pour Polytech (UCL, ULB, ULiège, UMons...)")

# 2. MENU LATÉRAL
menu = ["🔍 Recherche Annales (Arana)", "🤖 Assistant IA (Texte & Photo)", "📝 Aide Rapports", "💳 Version Premium"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- FONCTION DE NETTOYAGE LATEX ---
def clean_latex(text):
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- PAGE 1 : RECHERCHE ANNALES ---
if choice == "🔍 Recherche Annales (Arana)":
    st.subheader("Moteur de Recherche Sémantique d'Examens")
    try:
        df = pd.read_csv("data/examens.csv")
        col1, col2 = st.columns(2)
        with col1:
            univ_filter = st.multiselect("Université :", options=df["universite"].unique())
        with col2:
            search_query = st.text_input("Chercher un concept (ex: Moment d'inertie)")

        filtered_df = df
        if univ_filter:
            filtered_df = filtered_df[filtered_df["universite"].isin(univ_filter)]
        if search_query:
            filtered_df = filtered_df[filtered_df["concepts"].str.contains(search_query, case=False, na=False)]

        st.write(f"### {len(filtered_df)} Résultats")
        st.dataframe(filtered_df, use_container_width=True)
    except:
        st.info("Créez le fichier 'data/examens.csv' sur GitHub pour activer la recherche.")

# --- PAGE 2 : ASSISTANT IA VISION & TEXTE ---
elif choice == "🤖 Assistant IA (Texte & Photo)":
    st.subheader("Assistant IA Spécialisé Ingénierie")
    
    mode = st.radio("Méthode d'entrée :", ["Énoncé Texte", "Photo d'exercice / Schéma"])
    
    if mode == "Photo d'exercice / Schéma":
        uploaded_file = st.file_uploader("Upload la photo (PNG, JPG) :", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file, caption="Exercice chargé", width=300)
            if st.button("Analyser la photo"):
                with st.spinner("L'IA déchiffre l'exercice..."):
                    try:
                        base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                        completion = client.chat.completions.create(
                            model="llama-3.2-11b-vision-preview",
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyse cet exercice d'ingénieur. Explique la méthode de résolution étape par étape en LaTeX rigoureux."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }]
                        )
                        st.markdown("### 📘 Analyse de l'image :")
                        st.markdown(clean_latex(completion.choices[0].message.content))
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    else:
        user_prompt = st.text_area("Colle l'énoncé ici :", height=150)
        if st.button("Analyser le texte"):
            with st.spinner("Réflexion en cours..."):
                try:
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Tu es un tuteur expert en ingénierie. Réponds en LaTeX ($$ pour bloc, $ pour ligne)."},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    st.markdown("### 📘 Méthode proposée :")
                    st.markdown(clean_latex(chat_completion.choices[0].message.content))
                except Exception as e:
                    st.error(f"Erreur : {e}")

# --- PAGE 3 : AIDE RAPPORTS ---
elif choice == "📝 Aide Rapports":
    st.subheader("Générateur de Squelette de Rapport (LaTeX)")
    if st.button("Générer Template Standard"):
        st.code("\\documentclass{article}\n\\usepackage[utf8]{inputenc}\n\\title{Rapport d'Ingénierie}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\n\\section{Calculs}\n\\end{document}", language="latex")

# --- PAGE 4 : PREMIUM ---
elif choice == "💳 Version Premium":
    st.subheader("Accès Illimité & Corrigés")
    st.write("Débloque les corrigés d'examens et l'IA Vision illimitée.")
    st.link_button("S'abonner (9,99€/mois)", "https://www.lemonsqueezy.com")
