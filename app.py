import openai
import streamlit as st

# Configuración inicial de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Crear o recuperar asistente
assistant_id = st.secrets["ASSISTANT_ID"]
client = openai.Client(api_key=openai.api_key)

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id

st.title("🛍️ Agente de Reseñas de Productos")

# Campo para mensaje del usuario
user_input = st.text_input("Escribe aquí tu mensaje:")

# Botón para enviar mensaje
if st.button("Enviar mensaje"):
    if user_input:
        # Enviar mensaje del usuario al asistente
        client.beta.threads.messages.create(
            thread_id=st.session_state["thread_id"],
            role="user",
            content=user_input
        )

        # Ejecutar la respuesta del asistente
        run = client.beta.threads.runs.create_and_poll(
            thread_id=st.session_state["thread_id"],
            assistant_id=assistant_id
        )

        # Obtener respuesta del asistente
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state["thread_id"]
        )

        respuesta = messages.data[0].content[0].text.value

        st.markdown(f"🤖 **Agente:** {respuesta}")
