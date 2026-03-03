import streamlit as st
from groq import Groq

# 1. INITIALISATION (C'est ici qu'on définit 'client')
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Clé API manquante dans les Secrets Streamlit !")

st.set_page_config(page_title="Ingénieur OS", layout="wide")
st.title("🏗️ Ingénieur OS : Le Copilote du Bac 1")

# 2. NAVIGATION
menu = ["🔍 Recherche Annales", "🤖 Assistant IA (Méthodes)", "📝 Générateur Rapport"]
choice = st.sidebar.selectbox("Menu", menu)

# --- PAGE RECHERCHE ---
if choice == "🔍 Recherche Annales":
    st.subheader("Moteur de recherche multi-universités (Style Arana)")
    univ = st.multiselect("Filtrer par Univ :", ["UCL", "ULB", "ULiège", "UMons"])
    query = st.text_input("Rechercher un concept (ex: Moment d'inertie)")
    st.info("Bientôt : Indexation automatique des PDF d'examens.")

# --- PAGE ASSISTANT IA ---
elif choice == "🤖 Assistant IA (Méthodes)":
    st.subheader("Assistant Tuteur IA (No-Voice)")
    prompt = st.text_area("Pose ta question de maths ou physique :", placeholder="Ex: Comment résoudre une poutre en flexion ?")
    
    if st.button("Analyser la méthode"):
        if prompt:
            try:
                # Utilisation du modèle Llama 3.3 (Le plus récent et performant)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Tu es un tuteur pour ingénieurs. Réponds en LaTeX, sois très rigoureux, explique les étapes."},
                        {"role": "user", "content": prompt}
                    ],
                )

                st.markdown("### 📘 Méthode de résolution :")
                st.write(completion.choices.message.content)
            except Exception as e:
                st.error(f"Erreur de connexion à l'IA : {e}")
        else:
            st.warning("Veuillez entrer une question.")

# --- PAGE RAPPORTS ---
elif choice == "📝 Générateur Rapport":
    st.subheader("Aide à la rédaction de rapports et mémoires")
    if st.button("Générer un Template LaTeX (Standard Polytech)"):
        st.code("\\documentclass{article}\n\\usepackage[utf8]{inputenc}\n\\title{Rapport d'Ingénierie}\n\\begin{document}\n\\maketitle\n\\section{Introduction}\n\\end{document}", language='latex')
