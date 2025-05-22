import streamlit as st
import openai

# Load secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]
client = openai.Client()

# Set up session state
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id
    st.session_state["mensajes"] = []
    st.session_state["score"] = None
    st.session_state["conversacion_finalizada"] = False

st.title("🛍️ Agente de Reseñas de Productos")
st.markdown("Por favor, completa los datos del cliente y el producto para comenzar:")

# Formulario de inicio
with st.form("datos_form"):
    nombre = st.text_input("Nombre del cliente:")
    url = st.text_input("URL del producto:")
    score = st.slider("Puntaje entregado (1 a 5 estrellas):", 1, 5, 5)
    submitted = st.form_submit_button("Iniciar conversación con el asistente")

if submitted and nombre and url:
    st.session_state["score"] = score
    st.session_state["conversacion_finalizada"] = False
    mensaje_inicial = (
        f"{nombre} ha calificado el siguiente producto con {score} estrellas: {url}. "
        f"Como agente, ayúdalo a escribir una reseña completa. Haz preguntas breves, una a la vez, "
        f"para entender su experiencia y resaltar lo bueno del producto."
    )

    client.beta.threads.messages.create(
        thread_id=st.session_state["thread_id"],
        role="user",
        content=mensaje_inicial
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state["thread_id"],
        assistant_id=assistant_id
    )

    mensajes = client.beta.threads.messages.list(thread_id=st.session_state["thread_id"])

    # Get latest assistant message
    respuesta = None
    for mensaje in reversed(mensajes.data):
        if mensaje.role == "assistant" and mensaje.content:
            for item in mensaje.content:
                if item.type == "text":
                    respuesta = item.text.value
                    break
        if respuesta:
            break

    if respuesta:
        st.session_state["mensajes"].append(("agente", respuesta))
    else:
        st.session_state["mensajes"].append(("agente", "⚠️ El asistente no entregó una respuesta. Intenta recargar."))

# Mostrar historial de conversación
st.markdown("---")
st.subheader("🗣️ Conversación")

for rol, mensaje in st.session_state["mensajes"]:
    if rol == "agente":
        st.markdown(f"🤖 **Agente**: {mensaje}")
    else:
        st.markdown(f"🧑 **Tú**: {mensaje}")

# Input de usuario si la conversación sigue activa
if not st.session_state["conversacion_finalizada"]:
    user_input = st.text_input("Tu respuesta:", key="respuesta_input")

    if st.button("Enviar respuesta"):
        if user_input.strip() != "":
            st.session_state["mensajes"].append(("usuario", user_input))

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

            # Get latest assistant message
            respuesta = None
            for mensaje in reversed(mensajes.data):
                if mensaje.role == "assistant" and mensaje.content:
                    for item in mensaje.content:
                        if item.type == "text":
                            respuesta = item.text.value
                            break
                if respuesta:
                    break

            if respuesta:
                st.session_state["mensajes"].append(("agente", respuesta))
            else:
                st.session_state["mensajes"].append(("agente", "⚠️ El asistente no entregó una respuesta. Intenta recargar."))

            # Close after enough turns (adjust as needed)
            if len(st.session_state["mensajes"]) >= 6:
                st.session_state["conversacion_finalizada"] = True

            st.markdown("ℹ️ Si no ves una nueva respuesta, puedes recargar la página manualmente.")

# Mensaje de cierre según puntaje
if st.session_state["conversacion_finalizada"]:
    st.markdown("---")
    st.subheader("✅ Conversación finalizada")

    if st.session_state["score"] >= 4:
        st.success("🎉 ¡Gracias por tu opinión! Será de mucha utilidad para otros usuarios. "
                   "¡Esperamos que sigas disfrutando de tu producto!")
    elif st.session_state["score"] <= 2:
        st.error("😔 Lamentamos que tu experiencia no haya sido positiva. "
                 "Tu opinión ha sido derivada a nuestro equipo de atención al cliente para ayudarte a resolver el problema.")

