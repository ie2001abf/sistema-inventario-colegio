import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="Sistema de Inventario", page_icon="📚", layout="wide")

# DATOS DE SUPABASE - ¡ACTUALIZA ESTOS!
SUPABASE_URL = "https://cbwapocafiigqxbxpfok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNid2Fwb2NhZmlpZ3F4YnhwZm9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODUyNTcsImV4cCI6MjA5Njc2MTI1N30.Xzc_rB6tfx4j6A9nlBQgRoD-Wu8Tuz3VlYTRUsnPFhQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Título
st.title("📋 Sistema de Gestión de Inventario")

# Estado de sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==================== LOGIN ====================
if not st.session_state.logged_in:
    st.subheader("🔐 Inicio de Sesión")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        dni = st.text_input("DNI o Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", type="primary", use_container_width=True):
            if dni and password:
                # Buscar usuario por DNI
                try:
                    result = supabase.table("usuarios").select("*").eq("dni", dni).execute()
                    
                    if result.data:
                        user = result.data[0]
                        # Verificar contraseña (hash simple)
                        import hashlib
                        password_hash = hashlib.sha256(password.encode()).hexdigest()
                        
                        if user['password_hash'] == password_hash:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            # Actualizar último login
                            supabase.table("usuarios").update({
                                "ultimo_login": datetime.now().isoformat()
                            }).eq("id_usuario", user['id_usuario']).execute()
                            st.success(f"✅ ¡Bienvenido {user['nombres']}!")
                            st.rerun()
                        else:
                            st.error("❌ Contraseña incorrecta")
                    else:
                        st.error("❌ Usuario no encontrado")
                        
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
            else:
                st.warning("Ingresa tu DNI y contraseña")

# ==================== MENÚ PRINCIPAL ====================
else:
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.header(f"👋 Hola, {user['nombres']}")
        st.write(f"📧 {user['correo']}")
        st.divider()
        
        menu = st.radio(
            "📌 Menú Principal",
            ["📊 Dashboard", "🖥️ Ver Equipos", "➕ Agregar Equipo", "📈 Reportes"]
        )
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # Contenido según menú
    if menu == "📊 Dashboard":
        st.header("Dashboard")
        st.info("Bienvenido al panel de control")
        # Aquí pondrás las estadísticas
        
    elif menu == "🖥️ Ver Equipos":
        st.header("Listado de Equipos")
        response = supabase.table("equipos").select("*").limit(50).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No hay equipos registrados")
            
    elif menu == "➕ Agregar Equipo":
        st.header("Registrar Nuevo Equipo")
        with st.form("nuevo_equipo"):
            codigo = st.text_input("Código Patrimonial*")
            modelo = st.text_input("Modelo*")
            marca_id = st.number_input("ID Marca", min_value=1, step=1)
            tipo_id = st.number_input("ID Tipo", min_value=1, step=1)
            
            if st.form_submit_button("Guardar"):
                if codigo and modelo:
                    try:
                        supabase.table("equipos").insert({
                            "codigo_patrimonial": codigo,
                            "modelo": modelo,
                            "id_marca": marca_id,
                            "id_tipo": tipo_id
                        }).execute()
                        st.success("✅ Equipo guardado")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Completa los campos obligatorios")
    
    elif menu == "📈 Reportes":
        st.header("Reportes")
        st.info("Próximamente: reportes avanzados")