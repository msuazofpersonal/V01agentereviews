import streamlit as st
import openai
import os

openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

client = openai.Client()

# Crear un nuevo thread si no existe
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id

st.title("🛍️ Agente de Reseñas de Productos")

st.markdown("Por favor, completa los datos del cliente y el producto para comenzar:")

# Entradas del usuario
client_name = st.text_input("Nombre del cliente:")
product_url = st.text_input("URL del producto:")
score = st.slider("Puntaje entregado (1 a 5 estrellas):", 1, 5, 5)

# Botón para iniciar conversación
if st.button("Iniciar conversación con el asistente"):
    if client_name and product_url and score:
        # Crear mensaje inicial con contexto para el asistente
        mensaje_inicial = (
            f"{client_name} ha calificado el siguiente producto con {score} estrellas: {product_url}.\n"
            f"Como agente, ayúdalo a escribir una reseña completa. Haz preguntas breves, una a la vez, "
            f"para entender su experiencia y resaltar lo bueno del producto."
        )

        # Enviar mensaje al asistente
        client.beta.threads.messages.create(
            thread_id=st.session_state["thread_id"],
            role="user",
            content=mensaje_inicial
        )

        # Ejecutar y esperar respuesta
        run = client.beta.threads.runs.create_and_poll(
            thread_id=st.session_state["thread_id"],
            assistant_id=assistant_id
        )

        # Obtener y mostrar respuesta
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state["thread_id"]
        )
        respuesta = messages.data[0].content[0].text.value
        st.markdown(f"🤖 **Agente:** {respuesta}")

# Campo adicional para continuar la conversación
st.markdown("---")
user_reply = st.text_input("Tu respuesta al agente:")

if st.button("Enviar respuesta"):
    if user_reply:
        # Enviar respuesta del usuario
        client.beta.threads.messages.create(
            thread_id=st.session_state["thread_id"],
            role="user",
            content=user_reply
        )

        # Ejecutar siguiente paso del asistente
        run = client.beta.threads.runs.create_and_poll(
            thread_id=st.session_state["thread_id"],
            assistant_id=assistant_id
        )

        # Mostrar nueva respuesta
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state["thread_id"]
        )
        respuesta = messages.data[0].content[0].text.value
        st.markdown(f"🤖 **Agente:** {respuesta}")

