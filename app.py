import streamlit as st
import openai

# Inicializa OpenAI con secretos
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

client = openai.Client()

# Crea o recupera el hilo de conversación
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id
    st.session_state["mensajes"] = []  # para guardar el historial

st.title("🛍️ Agente de Reseñas de Productos")
st.markdown("Por favor, completa los datos del cliente y el producto para comenzar:")

# Inputs iniciales
with st.form("datos_form"):
    nombre = st.text_input("Nombre del cliente:")
    url = st.text_input("URL del producto:")
    score = st.slider("Puntaje entregado (1 a 5 estrellas):", 1, 5, 5)
    submitted = st.form_submit_button("Iniciar conversación con el asistente")

if submitted and nombre and url:
    mensaje_inicial = (
        f"{nombre} ha calificado el siguiente producto con {score} estrellas: {url}. "
        f"Como agente, ayúdalo a escribir una reseña completa. Haz preguntas breves, una a la vez, "
        f"para entender su experiencia y resaltar lo bueno del producto."
    )

    # Envía mensaje inicial
    client.beta.threads.messages.create(
        thread_id=st.session_state["thread_id"],
        role="user",
        content=mensaje_inicial
    )

    # Ejecuta el asistente
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state["thread_id"],
        assistant_id=assistant_id
    )

    # Muestra respuesta
    mensajes = client.beta.threads.messages.list(thread_id=st.session_state["thread_id"])
    respuesta = mensajes.data[0].content[0].text.value
    st.session_state["mensajes"].append(("agente", respuesta))

# Mostrar historial de conversación
st.markdown("---")
st.subheader("🗣️ Conversación")

for rol, mensaje in st.session_state["mensajes"]:
    if rol == "agente":
        st.markdown(f"🤖 **Agente**: {mensaje}")
    else:
        st.markdown(f"🧑 **Tú**: {mensaje}")

# Campo de entrada continua
user_input = st.text_input("Tu respuesta:", key="respuesta_input")

if st.button("Enviar respuesta"):
    if user_input.strip() != "":
        # Guarda mensaje del usuario
        st.session_state["mensajes"].append(("usuario", user_input))

        # Envia a OpenAI
        client.beta.threads.messages.create(
            thread_id=st.session_state["thread_id"],
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=st.session_state["thread_id"],
            assistant_id=assistant_id
        )

        mensajes = client.beta.threads.messages.list(thread_id=st.session_state["thread_id"])
        respuesta = mensajes.data[0].content[0].text.value
        st.session_state["mensajes"].append(("agente", respuesta))

        # Recarga la página automáticamente para mostrar el nuevo input
        st.experimental_rerun()
