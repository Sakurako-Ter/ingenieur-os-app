# --- 4. BARRE LATÉRALE (MENU) ---
st.sidebar.title("🚀 Ingénieur OS")
# Assure-toi que ces noms sont EXACTEMENT les mêmes plus bas
menu = ["🔍 Recherche Arana", "🤖 Assistant IA Multi", "📝 Rapports LaTeX", "💳 Version Premium"]
choice = st.sidebar.radio("Navigation", menu)

# --- 5. LOGIQUE DES PAGES ---

if choice == "🔍 Recherche Arana":
    st.title("🔍 Moteur de Recherche d'Examens")
    # ... (ton code de recherche)

elif choice == "🤖 Assistant IA Multi":
    st.title("🤖 Assistant IA Multi-supports")
    # ... (ton code IA)

# --- CETTE SECTION DOIT AVOIR LE MÊME NOM QUE DANS 'menu' ---
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

elif choice == "💳 Version Premium":
    st.title("💳 Version Premium")
    st.link_button("🚀 S'abonner", "https://www.lemonsqueezy.com")
