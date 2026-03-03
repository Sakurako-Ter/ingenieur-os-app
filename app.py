# --- PAGE 4 : ANALYSE DE FIABILITÉ (MULTI-SUPPORTS) ---
elif choice == "🛡️ Analyse de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité Scientifique")
    st.write("Vérifiez la crédibilité d'un document, d'un article ou d'une vidéo technique pour vos rapports.")

    # Choix du support de la source
    support = st.radio("Support à analyser :", ["Lien (Web / YouTube)", "Document PDF", "Extrait de texte"])
    sujet_travail = st.text_input("Sujet de votre travail de recherche :", placeholder="Ex: Étude de la portance d'une aile d'avion")

    source_data = "" # Initialisation du contenu à envoyer à l'IA

    # --- CAS 1 : LIEN WEB OU YOUTUBE ---
    if support == "Lien (Web / YouTube)":
        url = st.text_input("Collez l'URL de la source :", placeholder="https://youtube.com... ou https://article.com...")
        precisions = st.text_area("Optionnel : Ajoutez une transcription ou des détails sur l'auteur :", height=100)
        source_data = f"URL de la source : {url}\nPrécisions supplémentaires : {precisions}"
    
    # --- CAS 2 : DOCUMENT PDF ---
    elif support == "Document PDF":
        uploaded_pdf = st.file_uploader("Upload le PDF à auditer (Syllabus, Article, Note) :", type=["pdf"])
        if uploaded_pdf:
            with st.spinner("Lecture du document..."):
                try:
                    reader = PyPDF2.PdfReader(uploaded_pdf)
                    # Analyse des 3 premières pages (souvent suffisant pour l'autorité et l'intro)
                    pdf_text = ""
                    for i in range(min(3, len(reader.pages))):
                        pdf_text += reader.pages[i].extract_text()
                    source_data = f"Contenu extrait du PDF : {pdf_text[:8000]}" # Limite pour l'IA
                except Exception as e:
                    st.error(f"Erreur lors de la lecture du PDF : {e}")

    # --- CAS 3 : EXTRAIT DE TEXTE ---
    elif support == "Extrait de texte":
        source_data = st.text_area("Collez un extrait significatif de la source :", height=200, placeholder="Copiez-collez ici le texte à vérifier...")

    # --- BOUTON D'ACTION ---
    if st.button("Lancer l'audit de fiabilité"):
        if sujet_travail and source_data:
            with st.spinner("Expertise scientifique en cours..."):
                try:
                    # L'IA agit comme un examinateur d'intégrité académique
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": """Tu es un expert en intégrité académique pour ingénieurs. 
                            Ton rôle est d'analyser la source fournie et de rendre un verdict précis sur sa fiabilité.
                            Analyse selon ces axes :
                            1. 🔍 AUTORITÉ : Qui est l'auteur ou l'institution ? (Reconnu, Universitaire, ou Vulgarisation ?)
                            2. ⚙️ RIGUEUR : Y a-t-il une méthodologie, des calculs, des sources citées ?
                            3. ⚠️ BIAIS : La source est-elle objective ou commerciale/opinion ?
                            4. ⚖️ VERDICT FINAL : Note sur 10 et conseil ('Citer sans crainte', 'Citer avec prudence' ou 'À ÉVITER').
                            Sois critique et rigoureux."""},
                            {"role": "user", "content": f"Sujet de l'étudiant: {sujet_travail}\nDonnées de la source: {source_data}"}
                        ]
                    )
                    
                    st.markdown("---")
                    st.markdown("### 📊 Rapport d'Audit de Fiabilité")
                    # Affichage de la réponse (avec index 0 pour éviter l'erreur de liste)
                    st.markdown(res.choices[0].message.content)
                    
                    st.info("💡 **Note :** Un score élevé (8+) signifie que vous pouvez utiliser ce document comme référence solide dans votre bibliographie.")
                except Exception as e:
                    st.error(f"Erreur technique lors de l'analyse : {e}")
        else:
            st.warning("Veuillez remplir le sujet et fournir une source (Lien, PDF ou Texte).")
