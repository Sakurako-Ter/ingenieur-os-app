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
menu = ["🔍 Recherche Documents", "📝 Rapports LaTeX", "🛡️ Analyse de Fiabilité"]
choice = st.sidebar.radio("Navigation", menu)
st.sidebar.markdown("---")
st.sidebar.caption("Plateforme révolutionnaire pour le Bac 1 Ingénieur Civil.")

# --- 5. LOGIQUE DES PAGES ---

# --- PAGE 1 : RECHERCHE (ARANA) ---
if choice == "🔍 Recherche Documents":
    st.title("📚 Moteur de Recherche de Sources Certifiées")
    st.write("Trouvez des références académiques (articles, thèses, ouvrages) pour vos rapports.")
    
    query = st.text_input("Sujet scientifique (ex: Résistance des matériaux)", placeholder="Entrez un concept précis...")
    
    if query:
        with st.spinner("L'IA explore les bases de données académiques..."):
            try:
                res = client.chat.completions.create(
                    model="llama-3.2-70b-versatile",
                    messages=[
                        {"role": "system", "content": """Tu es un documentaliste expert. 
                        Pour le sujet donné, donne :
                        1. 📖 OUVRAGES : 2 livres classiques.
                        2. 🎓 THÈSES/ARTICLES : 2 ou 3 titres réels.
                        3. 🔗 LIENS : Liens cliquables vers Google Scholar/ResearchGate.
                        Réponds en LaTeX pour les formules."""},
                        {"role": "user", "content": f"Recherche approfondie : {query}"}
                    ]
                )
                
                st.markdown("### 🎯 Résultats de la recherche :")
                # LE [0] EST ICI POUR ÉVITER L'ERREUR
                st.markdown(render_math(res.choices[0].message.content))
                
            except Exception as e:
                st.error(f"Erreur de recherche : {e}")



# --- PAGE 2 : ASSISTANT IA (MULTI-SUPPORTS) ---
elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    st.write("Téléchargez un fichier (Image ou PDF) et posez votre question.")

    # Ton modèle stable confirmé
    MODÈLE_STABLE = "meta-llama/llama-4-scout-17b-16e-instruct"

    # 1. Zone de téléchargement unique (Photo ou PDF)
    uploaded_file = st.file_uploader(
        "Importer un exercice (Photo, Schéma ou PDF)", 
        type=['png', 'jpg', 'jpeg', 'pdf'],
        key="uploader_final_2026"
    )

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.info(f"📄 PDF chargé : {uploaded_file.name}")
        else:
            st.image(uploaded_file, caption="Aperçu du support", width=250)

    # 2. Zone de saisie (Style Math-GPT)
    prompt = st.chat_input("Posez votre question ici (ex: 'Résous l'exercice étape par étape')...")

    if prompt:
        with st.spinner(f"Analyse avec {MODÈLE_STABLE}..."):
            try:
                # --- LOGIQUE D'ANALYSE ---
                # CAS IMAGE
                if uploaded_file and uploaded_file.type != "application/pdf":
                    b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(
                        model=MODÈLE_STABLE, 
                        messages=[{"role":"user","content":[
                            {"type":"text","text": f"Analyse cette image et réponds en LaTeX : {prompt}"},
                            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                
                # CAS PDF
                elif uploaded_file and uploaded_file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(uploaded_file)
                    content = "".join([p.extract_text() for p in reader.pages[:3]])
                    res = client.chat.completions.create(
                        model=MODÈLE_STABLE,
                        messages=[{"role":"user","content":f"Contexte PDF : {content[:4000]}\n\nQuestion : {prompt}. Réponds en LaTeX."}]
                    )
                
                # CAS TEXTE SEUL
                else:
                    res = client.chat.completions.create(
                        model=MODÈLE_STABLE,
                        messages=[{"role":"system","content":"Tu es un expert ingénieur. Réponds en LaTeX."},
                                  {"role":"user","content":prompt}]
                    )

                # --- 3. AFFICHAGE AVEC POLICE RÉDUITE (CSS CIBLÉ) ---
                st.markdown("---")
                st.markdown("### 🎯 Solution :")
                
                reponse_ia = render_math(res.choices[0].message.content)
                
                st.markdown(f"""
                <style>
                    /* Réduction globale du texte de réponse */
                    .reponse-ia {{
                        font-size: 0.82rem !important; 
                        line-height: 1.5;
                        color: #e0e0e0;
                    }}
                    
                    /* Titres d'étapes (Etape 1, 2, 3...) */
                    .reponse-ia h1, .reponse-ia h2, .reponse-ia h3 {{
                        font-size: 0.9rem !important;
                        color: #2e7bc4 !important; /* Bleu pour les étapes */
                        margin-top: 15px !important;
                        margin-bottom: 5px !important;
                        font-weight: bold;
                    }}
                    
                    /* Mots importants ou numérotations en gras */
                    .reponse-ia strong {{
                        font-size: 0.85rem !important;
                        color: #5dade2;
                    }}

                    /* Listes à puces pour plus de clarté */
                    .reponse-ia li {{
                        margin-bottom: 4px;
                    }}
                </style>
                
                <div class="reponse-ia">
                    {reponse_ia}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")




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
            
