import streamlit as st
import pandas as pd
from groq import Groq
import base64
import PyPDF2
import io

# --- 1. CONFIGURATION ET CONNEXION IA ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. DESIGN & STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2e7bc4; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1e5ba0; border: 1px solid white; }
    div.stDataFrame { border-radius: 10px; overflow: hidden; }
    .stChatInput { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS UTILES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

# --- 4. BARRE LATÉRALE (MENU) ---
st.sidebar.title("🚀 Ingénieur OS")
st.sidebar.markdown("---")
menu = ["🔍 Recherche Documents", "🤖 Assistant IA Multi", "📝 Rapports LaTeX", "🛡️ Analyse de Fiabilité", "💳 Version Premium"]
choice = st.sidebar.radio("Navigation", menu)
st.sidebar.markdown("---")
st.sidebar.caption("Plateforme révolutionnaire pour le Bac 1 Ingénieur Civil.")

# --- 5. LOGIQUE DES PAGES ---

# --- PAGE 1 : RECHERCHE (ARANA) ---
if choice == "🔍 Recherche Arana":
    st.title("📚 Moteur de Recherche de Sources Certifiées")
    st.write("Trouvez des références semblables à votre document ou à un sujet précis.")
    
    # Zone mixte : Texte OU Fichier
    col_input, col_file = st.columns([2, 1])
    
    with col_input:
        query = st.text_input("Sujet scientifique :", placeholder="Ex: Résistance des matériaux...")
    
    with col_file:
        ref_file = st.file_uploader("Document source (PDF/Image)", type=['pdf', 'png', 'jpg', 'jpeg'])

    if st.button("Lancer la recherche de sources semblables"):
        extracted_context = ""
        
        with st.spinner("Analyse de votre document pour trouver des sources similaires..."):
            # 1. Extraction du contexte si un fichier est fourni
            if ref_file:
                if ref_file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(ref_file)
                    extracted_context = "".join([p.extract_text() for p in reader.pages[:2]])
                else:
                    b64 = base64.b64encode(ref_file.getvalue()).decode('utf-8')
                    res_vision = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role":"user","content":[
                            {"type":"text","text":"Extrais les concepts clés et le sujet scientifique de cette image pour une recherche bibliographique."},
                            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                    extracted_context = res_vision.choices[0].message.content

            # 2. Appel IA pour trouver des sources
            final_query = query if query else "ce document"
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": """Tu es un documentaliste expert en ingénierie.
                        Basé sur le texte ou l'image fournis, identifie des sources académiques réelles (Livres, Thèses, Articles).
                        Donne : 
                        1. 📖 2 Ouvrages de référence.
                        2. 🎓 3 Articles scientifiques réels.
                        3. 🔗 Liens directs vers Google Scholar."""},
                        {"role": "user", "content": f"Trouve des sources semblables à : {final_query}. Contexte extrait : {extracted_context[:2000]}"}
                    ]
                )
                
                st.markdown("### 🎯 Sources académiques recommandées :")
                st.markdown(render_math(res.choices[0].message.content))
                
            except Exception as e:
                st.error(f"Erreur : {e}")



# --- PAGE 2 : ASSISTANT IA (MULTI-SUPPORTS) ---
elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    st.write("Téléchargez un fichier (Image ou PDF) et posez votre question.")

    # Un seul sélecteur pour tous les types de fichiers
    uploaded_file = st.file_uploader(
        "Importer un exercice (Photo, Schéma ou PDF)", 
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Accepte les images (JPG, PNG) et les documents PDF"
    )

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.info(f"📄 PDF détecté : {uploaded_file.name}")
        else:
            st.image(uploaded_file, caption="Image détectée", width=300)

    # Zone de saisie toujours présente en bas
    prompt = st.chat_input("Posez votre question ici...")

    if prompt:
        with st.spinner("L'IA analyse votre demande..."):
            try:
                # SCÉNARIO 1 : C'EST UNE IMAGE
                if uploaded_file and uploaded_file.type != "application/pdf":
                    b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role":"user","content":[
                            {"type":"text","text": f"Question: {prompt}\nRéponds en utilisant LaTeX pour les formules."},
                            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                
                # SCÉNARIO 2 : C'EST UN PDF
                elif uploaded_file and uploaded_file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(uploaded_file)
                    content = "".join([p.extract_text() for p in reader.pages[:3]])
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"user","content":f"Analyse ce PDF d'ingénieur. Texte: {content[:4000]}\n\nQuestion: {prompt}. Réponds en LaTeX."}]
                    )
                
                # SCÉNARIO 3 : TEXTE SEUL
                else:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"system","content":"Tu es un tuteur ingénieur expert. Réponds toujours en LaTeX."},
                                  {"role":"user","content":prompt}]
                    )

                # Affichage du résultat
                st.markdown("---")
                st.markdown(render_math(res.choices[0].message.content))

            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {e}")


# --- PAGE 3 : RAPPORTS LATEX (CONVERSATIONNEL) ---
elif choice == "📝 Rapports LaTeX":
    st.title("📝 Copilote LaTeX Conversationnel")
    st.info("Explique ton projet (ex: 'Fais-moi un rapport de physique').")

    # Initialisation de la mémoire dans la session
    if "latex_chat" not in st.session_state:
        st.session_state.latex_chat = []

    # Affichage des messages
    for msg in st.session_state.latex_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de saisie
    if user_input := st.chat_input("Décris ton rapport ici..."):
        st.session_state.latex_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                # Appel IA
                messages = [{"role": "system", "content": "Expert LaTeX. Donne le code complet."}] + st.session_state.latex_chat
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
                full_code = res.choices.message.content
                
                st.code(full_code, language="latex")
                st.session_state.latex_chat.append({"role": "assistant", "content": full_code})
            except Exception as e:
                st.error(f"Erreur : {e}")

# --- PAGE 4 : ANALYSE DE FIABILITÉ ---
elif choice == "🛡️ Analyse de Fiabilité":
    st.title("🛡️ Analyseur de Fiabilité Scientifique")
    st.write("Vérifiez si un document ou une source est digne d'être cité dans un rapport d'ingénieur.")

    col1, col2 = st.columns(2)
    with col1:
        sujet_recherche = st.text_input("Sujet de votre travail :", placeholder="Ex: Étude de la fatigue de l'acier")
    with col2:
        type_doc = st.selectbox("Type de source :", ["Article Web", "Livre/Syllabus", "Vidéo/Blog", "Publication Scientifique"])

    doc_content = st.text_area("Collez ici un extrait du texte ou le nom/auteur de la source :", height=200)

    if st.button("Lancer l'audit de fiabilité"):
        if sujet_recherche and doc_content:
            with st.spinner("Analyse des critères de scientificité..."):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": """Tu es un expert en intégrité académique. 
                            Analyse la source fournie selon ces 4 critères :
                            1. AUTORITÉ : Qui est l'auteur/éditeur ? Est-il reconnu ?
                            2. RIGUEUR : Le langage est-il scientifique ? Y a-t-il des preuves/calculs ?
                            3. PERTINENCE : Est-ce adapté au sujet de recherche de l'étudiant ?
                            4. VERDICT : Note sur 10 et recommandation (Citer / Ne pas citer).
                            Réponds de manière concise et critique."""},
                            {"role": "user", "content": f"Sujet: {sujet_recherche}\nType: {type_doc}\nContenu à analyser: {doc_content}"}
                        ]
                    )
                    st.markdown("### 📊 Rapport d'Audit de la Source")
                    st.markdown(res.choices[0].message.content)
                    
                    st.success("💡 Conseil : Un score inférieur à 6/10 ne devrait pas figurer dans votre bibliographie officielle.")
                except Exception as e:
                    st.error(f"Erreur d'analyse : {e}")
        else:
            st.warning("Veuillez remplir le sujet et le contenu à analyser.")


# --- PAGE 5 : PREMIUM ---
elif choice == "💳 Version Premium":
    st.title("💳 Passez au Niveau Premium")
    st.markdown("""
    ### Débloquez la puissance totale :
    - ✅ **Recherche illimitée** dans toutes les archives d'examens.
    - ✅ **IA Vision & PDF sans limites** (Analyse de documents complets).
    - ✅ **Accès aux corrigés détaillés** rédigés par des tuteurs.
    """)
    st.link_button("🚀 S'abonner (9,99€ / mois)", "https://www.lemonsqueezy.com")
