import streamlit as st
import pandas as pd
from groq import Groq

# 1. INITIALISATION DU CLIENT IA
# Assure-toi d'avoir configuré GROQ_API_KEY dans Settings > Secrets sur Streamlit Cloud
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("⚠️ Clé API manquante ou mal configurée dans les Secrets Streamlit.")

# Configuration de la page
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

# Style CSS pour améliorer l'affichage
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Ingénieur OS : La Plateforme Révolutionnaire Bac 1")
st.caption("L'outil tout-en-un pour les futurs ingénieurs civils (UCL, ULB, ULiège, UMons...)")

# 2. MENU LATÉRAL (NAVIGATION)
menu = ["🔍 Recherche Annales (Arana)", "🤖 Assistant IA Tuteur", "📝 Aide Rapports & Mémoires", "💳 Version Premium"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- PAGE 1 : RECHERCHE ANNALES (STYLE ARANA) ---
if choice == "🔍 Recherche Annales (Arana)":
    st.subheader("Moteur de Recherche Sémantique d'Examens")
    
    # Chargement des données depuis le dossier data/
    try:
        df = pd.read_csv("data/examens.csv")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            univ_filter = st.multiselect("Filtrer par Université :", options=df["universite"].unique())
        with col2:
            search_query = st.text_input("Chercher un concept (ex: Moment d'inertie, Intégrales...)")

        # Filtrage
        temp_df = df
        if univ_filter:
            temp_df = temp_df[temp_df["universite"].isin(univ_filter)]
        if search_query:
            temp_df = temp_df[temp_df["concepts"].str.contains(search_query, case=False, na=False) | 
                              temp_df["matiere"].str.contains(search_query, case=False, na=False)]

        st.write(f"### {len(temp_df)} Ressources trouvées")
        # Affichage propre du tableau
        st.dataframe(temp_df, use_container_width=True)
        
    except Exception as e:
        st.warning("ℹ️ La base de données 'data/examens.csv' est vide ou en cours de création.")
        st.info("Crée le fichier 'data/examens.csv' sur GitHub pour activer la recherche.")

# --- PAGE 2 : ASSISTANT IA (AVEC NETTOYAGE LATEX) ---
elif choice == "🤖 Assistant IA Tuteur":
    st.subheader("Assistant IA Spécialisé Ingénierie (No-Voice)")
    st.write("Pose une question complexe, l'IA t'expliquera la méthodologie pas à pas.")
    
    user_prompt = st.text_area("Énoncé du problème :", height=150, placeholder="Ex: Comment calculer la flèche d'une poutre bi-encastrée ?")
    
    if st.button("Analyser et Résoudre"):
        if user_prompt:
            with st.spinner("L'IA analyse les lois de la physique..."):
                try:
                    # Requête à Groq avec Llama 3.3
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": """Tu es un tuteur expert en ingénierie civile. 
                            RÈGLES D'AFFICHAGE : 
                            1. Utilise TOUJOURS $$ ... $$ pour les formules mathématiques isolées.
                            2. Utilise TOUJOURS $ ... $ pour les variables dans le texte.
                            3. Ne donne pas la réponse brute, explique les étapes logiques. 
                            4. Réponds en français rigoureux."""},
                            {"role": "user", "content": user_prompt}
                        ],
                    )
                    
                    # Récupération et nettoyage du texte
                    raw_text = chat_completion.choices[0].message.content
                    clean_text = raw_text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")
                    
                    st.markdown("---")
                    st.markdown("### 📘 Méthode de résolution proposée :")
                    st.markdown(clean_text)
                    
                except Exception as e:
                    st.error(f"Erreur de connexion : {e}")
        else:
            st.warning("Entre une question pour obtenir de l'aide.")

# --- PAGE 3 : AIDE RAPPORTS ---
elif choice == "📝 Aide Rapports & Mémoires":
    st.subheader("Générateur de Structures de Rapports")
    type_rapport = st.selectbox("Type de document :", ["Rapport de Physique", "Projet d'Analyse", "Mémoire Technique"])
    
    if st.button("Générer le squelette LaTeX"):
        st.info("Copie ce code dans Overleaf pour un rendu professionnel.")
        template = """\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\title{Rapport de """ + type_rapport + """}
\\author{Étudiant Ingénieur}
\\begin{document}
\\maketitle
\\tableofcontents
\\section{Introduction}
\\section{Méthodologie}
\\section{Calculs et Résultats}
\\section{Conclusion}
\\end{document}"""
        st.code(template, language="latex")

# --- PAGE 4 : PREMIUM (ABONNEMENT) ---
elif choice == "💳 Version Premium":
    st.subheader("Passe au niveau supérieur")
    st.write("""
    **L'abonnement Premium te donne accès à :**
    - ✅ Corrigés détaillés de TOUS les examens (UCL, ULB, etc.)
    - ✅ IA sans limite de questions par jour
    - ✅ Modèles de rapports complets déjà rédigés
    """)
    
    # Remplacer par ton lien Lemon Squeezy plus tard
    st.link_button("S'abonner pour 9,99€ / mois", "https://www.lemonsqueezy.com")
