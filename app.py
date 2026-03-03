import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ingénieur OS", layout="wide")
st.title("🏗️ Ingénieur OS : Le Copilote du Bac 1")

menu = ["🔍 Recherche Annales", "🤖 Assistant IA (Méthodes)", "📝 Générateur Rapport"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "🔍 Recherche Annales":
    st.subheader("Moteur de recherche multi-universités")
    univ = st.multiselect("Filtrer par Univ :", ["UCL", "ULB", "ULiège", "UMons"])
    query = st.text_input("Rechercher un concept (ex: Moment d'inertie)")
    st.info("Résultats de recherche sémantique indexés...")

elif choice == "🤖 Assistant IA (Méthodes)":
    st.subheader("Assistant Tuteur (Zéro Bla-bla)")
    prompt = st.text_area("Colle ton énoncé ici pour obtenir la méthode de résolution :")
    if st.button("Analyser"):
        st.write("Analyse en cours via Llama-3 (Groq)...")

elif choice == "📝 Générateur Rapport":
    st.subheader("Outils de rédaction Mémoires & Rapports")
    if st.button("Générer Template LaTeX (Standard Ingé)"):
        st.code("\\documentclass{article}\n\\usepackage[utf8]{inputenc}\n\\begin{document}\n\\title{Rapport de Labo}\n\\maketitle\n\\end{document}")
