# -- coding: utf-8 --
import os
import re
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

st.set_page_config(
    page_title="Pizza 5 - Chatbot IA", 
    page_icon="🍕", 
    layout="centered"
)

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    try:
        API_KEY = st.secrets["GROQ_API_KEY"]
    except:
        st.error("⚠️ GROQ_API_KEY no configurada")
        st.stop()

os.environ["GROQ_API_KEY"] = API_KEY
client = Groq()

# Inicializar estados
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pedido_actual" not in st.session_state:
    st.session_state.pedido_actual = []
if "total_pedido" not in st.session_state:
    st.session_state.total_pedido = 0
if "edad_verificada" not in st.session_state:
    st.session_state.edad_verificada = False
if "pedido_confirmado" not in st.session_state:
    st.session_state.pedido_confirmado = False

PIZZERIA_INFO = {
    "nombre": "Pizza 5",
    "sucursal": "Av. Principal 1234, Lima, Perú",
    "horario": "Lunes a Domingo de 11:00 AM a 11:00 PM",
    "telefono": "01-555-7777",
    "whatsapp": "987-654-321",
    "delivery": "S/ 5 (Gratis en compras mayores a S/ 50)",
    "tiempo_entrega": "30-45 minutos"
}

SOCIOS = [
    "Brian Vargas Oros",
    "Felipe Jimenez Gutierrez",
    "Jhancarlo Florencio Silva Ochoa",
    "Julio Cesar Tejada Manrique",
    "Renzo Villalobos Cafferata"
]

MENU_PIZZAS = {
    "Clásicas": {
        "Margarita": {
            "descripcion": "Salsa de tomate, mozzarella fresca, albahaca",
            "precios": {"Personal": 22, "Mediana": 38, "Familiar": 55}
        },
        "Pepperoni": {
            "descripcion": "Salsa de tomate, mozzarella, pepperoni",
            "precios": {"Personal": 25, "Mediana": 42, "Familiar": 60}
        },
        "Hawaiana": {
            "descripcion": "Salsa de tomate, mozzarella, jamón, piña",
            "precios": {"Personal": 24, "Mediana": 40, "Familiar": 58}
        },
        "Napolitana": {
            "descripcion": "Salsa de tomate, mozzarella, anchoas, aceitunas",
            "precios": {"Personal": 26, "Mediana": 43, "Familiar": 62}
        }
    },
    "Especiales": {
        "Meat Lovers": {
            "descripcion": "Salsa de tomate, mozzarella, pepperoni, jamón, tocino, salchicha",
            "precios": {"Personal": 30, "Mediana": 50, "Familiar": 72}
        },
        "BBQ Chicken": {
            "descripcion": "Salsa BBQ, mozzarella, pollo, cebolla morada, tocino",
            "precios": {"Personal": 28, "Mediana": 48, "Familiar": 68}
        },
        "Vegetariana": {
            "descripcion": "Salsa de tomate, mozzarella, champiñones, pimientos, cebolla, aceitunas, tomate",
            "precios": {"Personal": 26, "Mediana": 44, "Familiar": 64}
        },
        "4 Quesos": {
            "descripcion": "Salsa blanca, mozzarella, parmesano, gorgonzola, queso de cabra",
            "precios": {"Personal": 29, "Mediana": 49, "Familiar": 70}
        }
    },
    "Premium": {
        "Trufa Negra": {
            "descripcion": "Salsa blanca, mozzarella, champiñones, trufa negra, rúcula",
            "precios": {"Personal": 35, "Mediana": 58, "Familiar": 85}
        },
        "Prosciutto e Rucola": {
            "descripcion": "Salsa de tomate, mozzarella, prosciutto, rúcula, parmesano",
            "precios": {"Personal": 33, "Mediana": 55, "Familiar": 80}
        },
        "Mariscos": {
            "descripcion": "Salsa blanca, mozzarella, camarones, calamares, mejillones, ajo",
            "precios": {"Personal": 36, "Mediana": 60, "Familiar": 88}
        }
    }
}

BORDES_ESPECIALES = {
    "Borde de Queso": 8,
    "Borde de Ajo": 6,
    "Borde de Hot Dog": 10
}

BEBIDAS_NO_ALCOHOLICAS = {
    "Inca Kola 1.5L": 8,
    "Coca-Cola 1.5L": 8,
    "Sprite 1.5L": 8,
    "Fanta 1.5L": 8,
    "Chicha Morada 1L": 6,
    "Limonada Natural 1L": 7,
    "Agua San Luis 600ml": 3,
    "Agua con Gas 600ml": 3
}

BEBIDAS_ALCOHOLICAS = {
    "Vinos": {
        "Vino Tinto Casillero del Diablo": 65,
        "Vino Blanco Santa Carolina": 60,
        "Vino Rosado Gato Negro": 55,
        "Vino Tinto Tacama Gran Reserva": 85,
        "Vino Blanco Tabernero": 50,
        "Copa de Vino Tinto": 18,
        "Copa de Vino Blanco": 16
    },
    "Cervezas": {
        "Cerveza Cusqueña 620ml": 12,
        "Cerveza Pilsen 620ml": 10,
        "Cerveza Corona 355ml": 14,
        "Cerveza Heineken 330ml": 13,
        "Cerveza Stella Artois 330ml": 15,
        "Cerveza Artesanal Barbarian 330ml": 18
    },
    "Whiskys": {
        "Whisky Johnnie Walker Red Label": 20,
        "Whisky Johnnie Walker Black Label": 28,
        "Whisky Jack Daniels": 25,
        "Whisky Chivas Regal 12 años": 32,
        "Whisky Old Parr": 30,
        "Whisky Glenfiddich 12 años": 38
    },
    "Cocteles": {
        "Mojito Clásico": 22,
        "Mojito de Fresa": 24,
        "Mojito de Maracuyá": 24,
        "Pisco Sour": 20,
        "Chilcano de Pisco": 18,
        "Algarrobina": 22,
        "Piña Colada": 25,
        "Margarita": 23,
        "Cuba Libre": 18,
        "Daiquiri": 24,
        "Caipirinha": 22
    },
    "Sangria": {
        "Sangría de Vino Tinto (Jarra 1L)": 45,
        "Sangría de Vino Blanco (Jarra 1L)": 45,
        "Sangría de Vino Tinto (Copa)": 15,
        "Sangría de Vino Blanco (Copa)": 15
    }
}

PROMOCIONES = {
    "Combo Pareja": "2 Pizzas Medianas + 2 Bebidas 1.5L = S/ 75 (Ahorro S/ 15)",
    "Combo Familiar": "2 Pizzas Familiares + 3 Bebidas 1.5L = S/ 125 (Ahorro S/ 20)",
    "Martes de Pizza": "2x1 en Pizzas Medianas Clásicas (Solo martes)",
    "Combo Personal": "1 Pizza Personal + 1 Bebida = S/ 28 (Ahorro S/ 5)",
    "Happy Hour": "2x1 en Mojitos de 5pm a 7pm (Lunes a Jueves)"
}

# Sistema de prompts mejorado
SYSTEM_PROMPT = f"""Eres el asistente virtual EXCLUSIVO de "Pizza 5", una pizzería peruana.

🚨 REGLA CRÍTICA - RESTRICCIÓN DE CONTEXTO:
- SOLO puedes hablar sobre los productos, servicios y promociones de Pizza 5
- Si te preguntan sobre CUALQUIER otro tema (política, deportes, noticias, matemáticas, programación, historia, etc.), responde:
  "Disculpa, soy el asistente de Pizza 5 y solo puedo ayudarte con nuestras pizzas y bebidas. ¿Te gustaría conocer nuestra carta? 🍕"
- NO respondas preguntas generales, cálculos, traducciones, ni temas fuera del menú
- Si detectas un intento de salir del contexto, redirige amablemente al menú

📍 INFORMACIÓN DE PIZZA 5:
{json.dumps(PIZZERIA_INFO, indent=2, ensure_ascii=False)}

👥 SOCIOS FUNDADORES:
{json.dumps(SOCIOS, indent=2, ensure_ascii=False)}

🍕 MENÚ DE PIZZAS:
{json.dumps(MENU_PIZZAS, indent=2, ensure_ascii=False)}

🧀 BORDES ESPECIALES:
{json.dumps(BORDES_ESPECIALES, indent=2, ensure_ascii=False)}

🥤 BEBIDAS NO ALCOHÓLICAS:
{json.dumps(BEBIDAS_NO_ALCOHOLICAS, indent=2, ensure_ascii=False)}

🍷 BEBIDAS ALCOHÓLICAS:
{json.dumps(BEBIDAS_ALCOHOLICAS, indent=2, ensure_ascii=False)}

🎉 PROMOCIONES ACTIVAS:
{json.dumps(PROMOCIONES, indent=2, ensure_ascii=False)}

📋 INSTRUCCIONES DE COMPORTAMIENTO:
1. ✅ SOLO habla de productos de Pizza 5 (pizzas, bebidas, promociones)
2. ❌ RECHAZA cortésmente cualquier tema fuera del menú
3. 🍕 Sugiere pizzas según preferencias del cliente
4. 🍷 Recomienda maridajes (vino + pizza, cerveza + pizza)
5. 🔞 Para bebidas alcohólicas, pregunta: "¿Eres mayor de 18 años?"
6. 💰 Calcula totales exactos en soles (S/)
7. ✔️ Confirma: producto, tamaño, cantidad, bordes extras
8. 📦 Pregunta: ¿Delivery o recojo? ¿Dirección? ¿Método de pago?
9. 😊 Tono amigable y peruano
10. 🎯 Usa emojis: 🍕🍷🍺🍹🎉

⚠️ RESTRICCIONES:
- Venta de alcohol SOLO a mayores de 18 años
- NO vendemos otros alimentos (hamburguesas, pastas, postres, etc.)
- NO respondas preguntas generales o académicas

💳 MÉTODOS DE PAGO: Efectivo, Tarjeta, Yape, Plin

Eres el MEJOR vendedor de Pizza 5. ¡Haz que cada cliente quiera ordenar! 🍕✨
"""

def extraer_pedido_del_texto(texto_usuario, texto_asistente):
    """Extrae productos mencionados SOLO del mensaje del usuario"""
    items_agregados = []
    texto_usuario_lower = texto_usuario.lower()
    
    # Palabras clave que indican una orden
    palabras_orden = ["quiero", "dame", "pido", "quisiera", "deseo", "me das", "voy a pedir", 
                      "ordenar", "agregar", "añadir", "también", "y un", "y una"]
    
    # Verificar que sea realmente un pedido
    es_pedido = any(palabra in texto_usuario_lower for palabra in palabras_orden)
    
    if not es_pedido:
        return items_agregados
    
    # Buscar pizzas SOLO en el texto del usuario
    for categoria in MENU_PIZZAS.values():
        for pizza, info in categoria.items():
            pizza_lower = pizza.lower()
            
            # Verificar que el nombre de la pizza esté en el mensaje del usuario
            if pizza_lower in texto_usuario_lower:
                # Buscar tamaño
                tamaño_encontrado = None
                for tamaño in ["personal", "mediana", "familiar"]:
                    if tamaño in texto_usuario_lower:
                        tamaño_encontrado = tamaño.capitalize()
                        break
                
                # Si no hay tamaño explícito, preguntar (no agregar automáticamente)
                if not tamaño_encontrado:
                    continue
                
                precio = info['precios'][tamaño_encontrado]
                
                # Buscar cantidad (solo números del 1-9 para evitar confusiones con precios)
                cantidad = 1
                numeros = re.findall(r'\b([1-9])\b', texto_usuario)
                if numeros:
                    cantidad = int(numeros[0])
                
                # Buscar borde
                borde = None
                precio_borde = 0
                for nombre_borde, precio_b in BORDES_ESPECIALES.items():
                    if nombre_borde.lower() in texto_usuario_lower:
                        borde = nombre_borde
                        precio_borde = precio_b
                        break
                
                item_desc = f"Pizza {pizza} {tamaño_encontrado}"
                if borde:
                    item_desc += f" + {borde}"
                if cantidad > 1:
                    item_desc += f" (x{cantidad})"
                
                precio_total = (precio + precio_borde) * cantidad
                
                items_agregados.append({
                    'descripcion': item_desc,
                    'precio': precio_total
                })
                
                # Importante: Agregar solo UNA vez cada pizza
                break
    
    # Buscar bebidas no alcohólicas SOLO en texto del usuario
    for bebida, precio in BEBIDAS_NO_ALCOHOLICAS.items():
        bebida_lower = bebida.lower()
        if bebida_lower in texto_usuario_lower:
            cantidad = 1
            numeros = re.findall(r'\b([1-9])\b', texto_usuario)
            if numeros and len(numeros) == 1:
                cantidad = int(numeros[0])
            
            item_desc = bebida
            if cantidad > 1:
                item_desc += f" (x{cantidad})"
            
            items_agregados.append({
                'descripcion': item_desc,
                'precio': precio * cantidad
            })
            break  # Solo agregar una vez
    
    # Buscar bebidas alcohólicas SOLO en texto del usuario
    if st.session_state.edad_verificada:
        for categoria in BEBIDAS_ALCOHOLICAS.values():
            for bebida, precio in categoria.items():
                bebida_lower = bebida.lower()
                if bebida_lower in texto_usuario_lower:
                    cantidad = 1
                    numeros = re.findall(r'\b([1-9])\b', texto_usuario)
                    if numeros and len(numeros) == 1:
                        cantidad = int(numeros[0])
                    
                    item_desc = bebida
                    if cantidad > 1:
                        item_desc += f" (x{cantidad})"
                    
                    items_agregados.append({
                        'descripcion': item_desc,
                        'precio': precio * cantidad
                    })
                    break  # Solo agregar una vez
    
    return items_agregados

def verificar_edad(texto):
    """Verifica si el usuario confirma ser mayor de edad"""
    confirmaciones = ["sí", "si", "yes", "claro", "obvio", "por supuesto", "tengo", "soy mayor"]
    texto_lower = texto.lower()
    
    # Buscar números de edad
    numeros = re.findall(r'\b(\d{2})\b', texto)
    if numeros:
        edad = int(numeros[0])
        if edad >= 18:
            return True
    
    # Buscar confirmaciones
    for conf in confirmaciones:
        if conf in texto_lower:
            return True
    
    return False

# Estilos CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #2C1810 0%, #4A2C1A 100%);
    }
    h1 {
        color: #FF6B35;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        padding: 20px;
        background: linear-gradient(90deg, #8B0000 0%, #FF4500 100%);
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .socios-box {
        background-color: rgba(255, 107, 53, 0.1);
        border: 2px solid #FF6B35;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #FFE4B5;
    }
    .pedido-box {
        background-color: rgba(255, 215, 0, 0.1);
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B35;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #FF4500;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🍕🍷 Pizza 5 - Asistente Virtual</h1>", unsafe_allow_html=True)

st.markdown(f"""
    <div class="socios-box">
        <h3 style="color: #FF6B35; text-align: center;">👥 Nuestros Socios Fundadores</h3>
        <ul style="color: #FFE4B5;">
            {''.join([f"<li>{socio}</li>" for socio in SOCIOS])}
        </ul>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🍕 Pizza 5")
    st.markdown(f"**📍** {PIZZERIA_INFO['sucursal']}")
    st.markdown(f"**🕐** {PIZZERIA_INFO['horario']}")
    st.markdown("---")
    st.markdown(f"**📞** {PIZZERIA_INFO['telefono']}")
    st.markdown(f"**💬** WhatsApp: {PIZZERIA_INFO['whatsapp']}")
    st.markdown(f"**🏍️** {PIZZERIA_INFO['delivery']}")
    st.markdown(f"**⏱️** {PIZZERIA_INFO['tiempo_entrega']}")
    
    st.markdown("---")
    st.markdown("### 🎉 Promociones")
    for promo, detalle in PROMOCIONES.items():
        st.markdown(f"**{promo}**")
        st.caption(detalle)
    
    st.markdown("---")
    st.markdown("### 🍕 Carta Completa")
    
    with st.expander("🍕 Pizzas Clásicas"):
        for pizza, info in MENU_PIZZAS["Clásicas"].items():
            st.markdown(f"**{pizza}**")
            st.caption(info['descripcion'])
            st.text(f"Personal: S/{info['precios']['Personal']} | Mediana: S/{info['precios']['Mediana']} | Familiar: S/{info['precios']['Familiar']}")
    
    with st.expander("⭐ Pizzas Especiales"):
        for pizza, info in MENU_PIZZAS["Especiales"].items():
            st.markdown(f"**{pizza}**")
            st.caption(info['descripcion'])
            st.text(f"Personal: S/{info['precios']['Personal']} | Mediana: S/{info['precios']['Mediana']} | Familiar: S/{info['precios']['Familiar']}")
    
    with st.expander("👑 Pizzas Premium"):
        for pizza, info in MENU_PIZZAS["Premium"].items():
            st.markdown(f"**{pizza}**")
            st.caption(info['descripcion'])
            st.text(f"Personal: S/{info['precios']['Personal']} | Mediana: S/{info['precios']['Mediana']} | Familiar: S/{info['precios']['Familiar']}")
    
    with st.expander("🧀 Bordes Especiales"):
        for borde, precio in BORDES_ESPECIALES.items():
            st.markdown(f"**{borde}** - S/ {precio}")
    
    with st.expander("🥤 Bebidas No Alcohólicas"):
        for bebida, precio in BEBIDAS_NO_ALCOHOLICAS.items():
            st.markdown(f"{bebida} - S/ {precio}")
    
    with st.expander("🍷 Bebidas Alcohólicas (+18)"):
        st.markdown("**Vinos**")
        for vino, precio in BEBIDAS_ALCOHOLICAS["Vinos"].items():
            st.text(f"{vino} - S/ {precio}")
        
        st.markdown("**Whiskys**")
        for whisky, precio in BEBIDAS_ALCOHOLICAS["Whiskys"].items():
            st.text(f"{whisky} - S/ {precio}")
        
        st.markdown("**Cocteles**")
        for coctel, precio in BEBIDAS_ALCOHOLICAS["Cocteles"].items():
            st.text(f"{coctel} - S/ {precio}")
        
        st.markdown("**Cervezas**")
        for cerveza, precio in BEBIDAS_ALCOHOLICAS["Cervezas"].items():
            st.text(f"{cerveza} - S/ {precio}")
        
        st.markdown("**Sangría**")
        for sangria, precio in BEBIDAS_ALCOHOLICAS["Sangria"].items():
            st.text(f"{sangria} - S/ {precio}")
    
    st.markdown("---")
    
    # Mostrar pedido actual
    if st.session_state.pedido_actual:
        st.markdown("### 🛒 Tu Pedido Actual")
        st.markdown('<div class="pedido-box">', unsafe_allow_html=True)
        for item in st.session_state.pedido_actual:
            st.markdown(f"✓ {item['descripcion']} - S/ {item['precio']:.2f}")
        st.markdown(f"**💰 Total: S/ {st.session_state.total_pedido:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirmar Pedido", use_container_width=True):
                st.session_state.pedido_confirmado = True
                whatsapp_msg = f"Hola Pizza 5! Quiero confirmar mi pedido:\n\n"
                for item in st.session_state.pedido_actual:
                    whatsapp_msg += f"• {item['descripcion']} - S/{item['precio']:.2f}\n"
                whatsapp_msg += f"\nTotal: S/{st.session_state.total_pedido:.2f}"
                whatsapp_url = f"https://wa.me/51{PIZZERIA_INFO['whatsapp'].replace('-','')}?text={whatsapp_msg}"
                st.markdown(f"[📱 Enviar por WhatsApp]({whatsapp_url})")
                st.success("✅ Pedido confirmado! Envíalo por WhatsApp")
        
        with col2:
            if st.button("🗑️ Limpiar Pedido", use_container_width=True):
                st.session_state.pedido_actual = []
                st.session_state.total_pedido = 0
                st.rerun()
    
    st.markdown("---")
    if st.button("🔄 Nueva Conversación", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pedido_actual = []
        st.session_state.total_pedido = 0
        st.session_state.edad_verificada = False
        st.session_state.pedido_confirmado = False
        st.rerun()

# Historial de chat
for msg in st.session_state.chat_history:
    avatar = "🍕" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Input del usuario
user_input = st.chat_input("💬 Escribe tu pedido aquí... 🍕🍷")

if user_input:
    # Validar longitud
    if len(user_input) > 500:
        st.error("⚠️ Mensaje muy largo. Por favor, sé más conciso.")
        st.stop()
    
    # Agregar mensaje del usuario
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    # Verificar edad para bebidas alcohólicas
    if not st.session_state.edad_verificada:
        if verificar_edad(user_input):
            st.session_state.edad_verificada = True
    
    # Preparar mensajes para la API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(st.session_state.chat_history)
    
    try:
        with st.spinner("🍕 Preparando tu respuesta..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            respuesta_texto = response.choices[0].message.content
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {str(e)}")
        respuesta_texto = f"🍕 Disculpa, tenemos problemas técnicos. Por favor, llámanos al {PIZZERIA_INFO['telefono']} o escríbenos al WhatsApp {PIZZERIA_INFO['whatsapp']}"
    
    with st.chat_message("assistant", avatar="🍕"):
        st.markdown(respuesta_texto)
    
    st.session_state.chat_history.append({"role": "assistant", "content": respuesta_texto})
    
    # Extraer productos del pedido
    nuevos_items = extraer_pedido_del_texto(user_input, respuesta_texto)
    if nuevos_items:
        for item in nuevos_items:
            st.session_state.pedido_actual.append(item)
            st.session_state.total_pedido += item['precio']
        st.rerun()

# Mensaje inicial
if not st.session_state.chat_history:
    mensaje_inicial = """¡Hola! Bienvenido a **Pizza 5** 🍕🍷

Somos una pizzería peruana fundada por 5 socios apasionados por la buena comida.

**¿Qué ofrecemos?**
🍕 Pizzas (Clásicas, Especiales y Premium)
🍷 Vinos selectos
🍺 Cervezas nacionales e importadas
🥃 Whiskys premium
🍹 Cocteles deliciosos
🍇 Sangría refrescante

🎉 **Promoción Especial:**
💫 Happy Hour: 2x1 en Mojitos de 5pm-7pm (Lun-Jue)
💫 Martes de Pizza: 2x1 en Pizzas Medianas Clásicas

⚠️ *Bebidas alcohólicas solo para mayores de 18 años*

¿Qué te gustaría ordenar hoy? 😊🍕"""
    
    with st.chat_message("assistant", avatar="🍕"):
        st.markdown(mensaje_inicial)
    
    st.session_state.chat_history.append({"role": "assistant", "content": mensaje_inicial})