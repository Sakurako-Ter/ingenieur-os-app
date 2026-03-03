import streamlit as st
from groq import Groq
import base64
import PyPDF2
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Ingénieur OS", page_icon="🏗️", layout="wide")

# Initialisation de la clé API Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("⚠️ Erreur : Configurez votre GROQ_API_KEY dans les Secrets Streamlit.")

# --- 2. INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. DESIGN & STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #2e7bc4; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1e5ba0; border: 1px solid white; }
    .home-card {
        background-color: #1e2130; padding: 20px; border-radius: 15px;
        border-left: 5px solid #2e7bc4; margin-bottom: 20px; height: 180px;
    }
    .main-title { font-size: 3.5rem; font-weight: bold; color: #2e7bc4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS UTILES ---
def render_math(text):
    if not text: return ""
    return text.replace("\[", "$$").replace("\]", "$$").replace("\(", "$").replace("\)", "$")

def reset_chat():
    st.session_state.messages = []
    st.rerun()

# --- 5. BARRE LATÉRALE (NAVIGATION) ---
st.sidebar.title("🚀 Ingénieur OS")
st.sidebar.markdown("---")
menu = ["🏠 Accueil", "🤖 Assistant IA Conversationnel", "🔍 Recherche Arana", "📝 Rapports LaTeX", "🛡️ Analyse de Fiabilité", "💳 Version Premium"]
choice = st.sidebar.radio("Navigation", menu)

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Nouvelle Conversation"):
    reset_chat()

st.sidebar.caption("Plateforme pour le Bac 1 Ingénieur Civil.")

# --- 6. LOGIQUE DES PAGES ---

# --- PAGE ACCUEIL ---
if choice == "🏠 Accueil":
    st.markdown('<h1 class="main-title">🏗️ Ingénieur OS</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>L'écosystème intelligent dédié à la réussite en Polytechnique.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="home-card"><h3>🤖 Assistant Multi-Support</h3><p>Discutez avec une IA experte qui comprend vos textes, vos photos d\'exercices et vos syllabus PDF.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="home-card"><h3>🔍 Recherche Arana</h3><p>Accédez à des sources académiques certifiées (livres, thèses) pour vos travaux de recherche.</p></div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="home-card"><h3>📝 Rapports LaTeX</h3><p>Générez des structures de rapports scientifiques impeccables et prêtes à être compilées.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="home-card"><h3>🛡️ Analyse de Fiabilité</h3><p>Vérifiez la rigueur scientifique de vos sources avant de les citer dans vos projets.</p></div>', unsafe_allow_html=True)

    if st.button("🚀 Commencer à travailler"):
        st.info("Sélectionnez un outil dans le menu de gauche !")

# --- PAGE 1 : ASSISTANT IA CONVERSATIONNEL ---
elif choice == "🤖 Assistant IA Conversationnel":
    st.title("🤖 Assistant IA Multi-support")
    
    tab1, tab2, tab3 = st.tabs(["💬 Conversation continue", "📸 Analyse Photo", "📂 Analyse PDF"])

    with tab1:
        # Affichage de l'historique
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(render_math(message["content"]))

        # Input utilisateur
        if prompt := st.chat_input("Posez votre question (ex: calcul de structure, physique...)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Tu es un tuteur expert en ingénierie. Réponds en utilisant LaTeX pour toutes les formules mathématiques."}] + st.session_state.messages
                    )
                    full_res = res.choices[0].message.content
                    st.markdown(render_math(full_res))
                    st.session_state.messages.append({"role": "assistant", "content": full_res})
                except Exception as e:
                    st.error(f"Erreur API : {e}")

    with tab2:
        img = st.file_uploader("Télécharger une photo de l'exercice :", type=['png', 'jpg', 'jpeg'])
        if img and st.button("Analyser l'image"):
            with st.spinner("Analyse visuelle en cours..."):
                b64 = base64.b64encode(img.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{"role":"user","content":[
                        {"type":"text","text":"Analyse cet exercice et donne la solution détaillée en LaTeX."},
                        {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                analysis = res.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": f"[Analyse Image] : {analysis}"})
                st.markdown(render_math(analysis))
                st.info("L'analyse a été ajoutée à la conversation continue.")

    with tab3:
        pdf = st.file_uploader("Charger un syllabus (PDF) :", type=['pdf'])
        if pdf and st.button("Extraire les concepts clés"):
            reader = PyPDF2.PdfReader(pdf)
            text_content = "".join([p.extract_text() for p in reader.pages[:3]])
            context_prompt = f"Voici un extrait de mon cours. Peux-tu le résumer et te préparer à répondre à mes questions dessus ?\n\nContenu : {text_content[:3000]}"
            st.session_state.messages.append({"role": "user", "content": context_prompt})
            st.success("Syllabus analysé ! Vous pouvez maintenant poser vos questions dans l'onglet 'Conversation'.")

# --- PAGE 2 : RECHERCHE ARANA ---
elif choice == "🔍 Recherche Arana":
    st.title("📚 Recherche de Sources Certifiées")
    query = st.text_input("Sujet scientifique :", placeholder="ex: Mécanique des fluides")
    if query:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Documentaliste expert. Donne 2 livres et 2 articles réels avec liens Scholar."},
                      {"role": "user", "content": f"Recherche : {query}"}]
        )
        st.markdown(render_math(res.choices[0].message.content))

# --- PAGE 3 : RAPPORTS LATEX ---
elif choice == "📝 Rapports LaTeX":
    st.title("📝 Générateur de Code LaTeX")
    user_req = st.text_area("Décris ton rapport (ex: TP de Physique sur le pendule) :")
    if st.button("Générer le template"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Expert LaTeX. Donne uniquement le code complet."},
                      {"role": "user", "content": user_req}]
        )
        st.code(res.choices[0].message.content, language="latex")

# --- PAGE 4 : ANALYSE DE FIABILITÉ ---
elif choice == "🛡️ Analyse de Fiabilité":
    st.title("🛡️ Audit de Fiabilité Scientifique")
    source_text = st.text_area("Collez l'extrait ou la source à vérifier :")
    if st.button("Lancer l'audit"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Expert en intégrité scientifique. Note la source sur 10."},
                      {"role": "user", "content": source_text}]
        )
        st.write(res.choices[0].message.content)

# --- PAGE 5 : PREMIUM ---
elif choice == "💳 Version Premium":
    st.title("💳 Passez au niveau supérieur")
    st.success("Accès illimité aux modèles Llama 3 Vision et export PDF direct.")
    st.button("S'abonner (Prochainement)")
