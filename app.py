import streamlit as st
from supabase import create_client
import pandas as pd
import hashlib
import re
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE SUPABASE - CREDENCIALES CORRECTAS
# ============================================
SUPABASE_URL = "https://cbwapocafiigqxbxpfok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNid2Fwb2NhZmlpZ3F4YnhwZm9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODUyNTcsImV4cCI6MjA5Njc2MTI1N30.Xzc_rB6tfx4j6A9nlBQgRoD-Wu8Tuz3VlYTRUsnPFhQ"
# ============================================

# Inicializar conexión
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def hash_password(password):
    """Hashea la contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validar_dni(dni):
    """Valida DNI: solo números, 8 caracteres, no vacío"""
    if not dni:
        return False, "El DNI no puede estar vacío"
    if not dni.isdigit():
        return False, "El DNI debe contener solo números"
    if len(dni) != 8:
        return False, "El DNI debe tener exactamente 8 dígitos"
    return True, ""

def limpiar_nombre(texto):
    """Limpia espacios y capitaliza primera letra de cada palabra"""
    if not texto:
        return ""
    texto = texto.strip()
    palabras = texto.split()
    palabras = [p.capitalize() for p in palabras]
    return " ".join(palabras)

def limpiar_texto_normal(texto):
    """Limpia espacios y capitaliza primera letra (para descripciones)"""
    if not texto:
        return ""
    texto = texto.strip()
    palabras = texto.split()
    palabras = [p.capitalize() for p in palabras]
    return " ".join(palabras)

def validar_correo(correo):
    """Valida formato de correo electrónico"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not correo:
        return False, "El correo no puede estar vacío"
    if not re.match(patron, correo):
        return False, "Formato de correo inválido"
    return True, ""

def obtener_perfiles():
    """Obtiene lista de perfiles para el desplegable"""
    try:
        response = supabase.table("perfiles").select("id_perfil, nombre_perfil").eq("activo", True).execute()
        if response.data:
            return {p["nombre_perfil"]: p["id_perfil"] for p in response.data}
        return {"Administrador": 1, "Jefe de Inventario": 2, "Inventariador": 3, "Docente": 4, "Consulta": 5}
    except:
        return {"Administrador": 1, "Jefe de Inventario": 2, "Inventariador": 3, "Docente": 4, "Consulta": 5}

def obtener_perfil_nombre(id_perfil):
    """Obtiene el nombre del perfil por ID"""
    perfiles = obtener_perfiles()
    for nombre, pid in perfiles.items():
        if pid == id_perfil:
            return nombre
    return "Desconocido"

# ============================================
# FUNCIONES CRUD PARA TIPO DE EQUIPOS
# ============================================

def listar_tipos_equipos():
    """Obtiene lista de todos los tipos de equipos"""
    try:
        response = supabase.table("tipo_equipos").select("*").order("id_tipo", asc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al listar tipos de equipo: {e}")
        return []

def crear_tipo_equipo(descripcion, categoria, vida_util_anios):
    """Crea un nuevo tipo de equipo"""
    if not descripcion:
        return False, "La descripción es obligatoria"
    if not categoria:
        return False, "La categoría es obligatoria"
    
    descripcion_limpia = limpiar_texto_normal(descripcion)
    categoria_limpia = limpiar_texto_normal(categoria)
    
    # Verificar si ya existe
    existe = supabase.table("tipo_equipos").select("id_tipo").eq("descripcion", descripcion_limpia).execute()
    if existe.data:
        return False, f"Ya existe un tipo de equipo con descripción '{descripcion_limpia}'"
    
    nuevo_tipo = {
        "descripcion": descripcion_limpia,
        "categoria": categoria_limpia,
        "vida_util_anios": vida_util_anios,
        "activo": True,
        "creado_en": datetime.now().isoformat()
    }
    
    try:
        result = supabase.table("tipo_equipos").insert(nuevo_tipo).execute()
        if result.data:
            return True, f"Tipo de equipo '{descripcion_limpia}' creado exitosamente"
        return False, "Error al crear el tipo de equipo"
    except Exception as e:
        return False, f"Error en la base de datos: {str(e)}"

def actualizar_tipo_equipo(id_tipo, descripcion, categoria, vida_util_anios, activo):
    """Actualiza un tipo de equipo existente"""
    if not descripcion:
        return False, "La descripción es obligatoria"
    if not categoria:
        return False, "La categoría es obligatoria"
    
    descripcion_limpia = limpiar_texto_normal(descripcion)
    categoria_limpia = limpiar_texto_normal(categoria)
    
    # Verificar si ya existe otro con la misma descripción
    existe = supabase.table("tipo_equipos").select("id_tipo").eq("descripcion", descripcion_limpia).neq("id_tipo", id_tipo).execute()
    if existe.data:
        return False, f"Ya existe otro tipo de equipo con descripción '{descripcion_limpia}'"
    
    try:
        result = supabase.table("tipo_equipos").update({
            "descripcion": descripcion_limpia,
            "categoria": categoria_limpia,
            "vida_util_anios": vida_util_anios,
            "activo": activo,
            "actualizado_en": datetime.now().isoformat()
        }).eq("id_tipo", id_tipo).execute()
        
        if result.data:
            return True, "Tipo de equipo actualizado exitosamente"
        return False, "Error al actualizar tipo de equipo"
    except Exception as e:
        return False, f"Error: {str(e)}"

def eliminar_tipo_equipo(id_tipo):
    """Elimina un tipo de equipo (soft delete - lo desactiva)"""
    try:
        result = supabase.table("tipo_equipos").update({"activo": False}).eq("id_tipo", id_tipo).execute()
        if result.data:
            return True, "Tipo de equipo desactivado exitosamente"
        return False, "Error al desactivar tipo de equipo"
    except Exception as e:
        return False, f"Error: {str(e)}"

def reactivar_tipo_equipo(id_tipo):
    """Re-activa un tipo de equipo desactivado"""
    try:
        result = supabase.table("tipo_equipos").update({"activo": True}).eq("id_tipo", id_tipo).execute()
        if result.data:
            return True, "Tipo de equipo reactivado exitosamente"
        return False, "Error al reactivar tipo de equipo"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ============================================
# FUNCIONES CRUD PARA USUARIOS
# ============================================

def crear_usuario(dni, nombres, apellidos, correo, password, id_perfil):
    """Crea un nuevo usuario en la base de datos"""
    valido, mensaje = validar_dni(dni)
    if not valido:
        return False, mensaje
    
    if not nombres or not apellidos:
        return False, "Nombres y apellidos son obligatorios"
    
    valido, mensaje = validar_correo(correo)
    if not valido:
        return False, mensaje
    
    if not password or len(password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres"
    
    nombres_limpio = limpiar_nombre(nombres)
    apellidos_limpio = limpiar_nombre(apellidos)
    correo_limpio = correo.strip().lower()
    password_hash = hash_password(password)
    
    # Verificar si el DNI ya existe
    existe = supabase.table("usuarios").select("id_usuario").eq("dni", dni).execute()
    if existe.data:
        return False, f"Ya existe un usuario con DNI {dni}"
    
    # Verificar si el correo ya existe
    existe_correo = supabase.table("usuarios").select("id_usuario").eq("correo", correo_limpio).execute()
    if existe_correo.data:
        return False, f"Ya existe un usuario con correo {correo_limpio}"
    
    nuevo_usuario = {
        "dni": dni,
        "nombres": nombres_limpio,
        "apellidos": apellidos_limpio,
        "correo": correo_limpio,
        "password_hash": password_hash,
        "id_perfil": id_perfil,
        "activo": True,
        "creado_en": datetime.now().isoformat()
    }
    
    try:
        result = supabase.table("usuarios").insert(nuevo_usuario).execute()
        if result.data:
            return True, f"Usuario {nombres_limpio} {apellidos_limpio} creado exitosamente"
        return False, "Error al crear el usuario"
    except Exception as e:
        return False, f"Error en la base de datos: {str(e)}"

def listar_usuarios():
    """Obtiene lista de todos los usuarios"""
    try:
        response = supabase.table("usuarios").select("*").order("creado_en", desc=True).execute()
        return response.data if response.data else []
    except:
        return []

def actualizar_usuario(id_usuario, datos):
    """Actualiza datos de un usuario"""
    try:
        existe = supabase.table("usuarios").select("id_usuario").eq("id_usuario", id_usuario).execute()
        if not existe.data:
            return False, "Usuario no encontrado"
        
        result = supabase.table("usuarios").update(datos).eq("id_usuario", id_usuario).execute()
        if result.data:
            return True, "Usuario actualizado exitosamente"
        return False, "Error al actualizar usuario"
    except Exception as e:
        return False, f"Error: {str(e)}"

def actualizar_datos_usuario(id_usuario, dni, nombres, apellidos, correo, id_perfil):
    """Actualiza todos los datos de un usuario"""
    valido, mensaje = validar_dni(dni)
    if not valido:
        return False, mensaje
    
    if not nombres or not apellidos:
        return False, "Nombres y apellidos son obligatorios"
    
    valido, mensaje = validar_correo(correo)
    if not valido:
        return False, mensaje
    
    nombres_limpio = limpiar_nombre(nombres)
    apellidos_limpio = limpiar_nombre(apellidos)
    correo_limpio = correo.strip().lower()
    
    # Verificar si el DNI ya existe en otro usuario
    existe_dni = supabase.table("usuarios").select("id_usuario").eq("dni", dni).neq("id_usuario", id_usuario).execute()
    if existe_dni.data:
        return False, f"Ya existe otro usuario con DNI {dni}"
    
    # Verificar si el correo ya existe en otro usuario
    existe_correo = supabase.table("usuarios").select("id_usuario").eq("correo", correo_limpio).neq("id_usuario", id_usuario).execute()
    if existe_correo.data:
        return False, f"Ya existe otro usuario con correo {correo_limpio}"
    
    try:
        result = supabase.table("usuarios").update({
            "dni": dni,
            "nombres": nombres_limpio,
            "apellidos": apellidos_limpio,
            "correo": correo_limpio,
            "id_perfil": id_perfil,
            "actualizado_en": datetime.now().isoformat()
        }).eq("id_usuario", id_usuario).execute()
        
        if result.data:
            return True, "Usuario actualizado exitosamente"
        return False, "Error al actualizar usuario"
    except Exception as e:
        return False, f"Error: {str(e)}"

def eliminar_usuario(id_usuario):
    """Elimina un usuario (soft delete - lo desactiva)"""
    try:
        result = supabase.table("usuarios").update({"activo": False}).eq("id_usuario", id_usuario).execute()
        if result.data:
            return True, "Usuario desactivado exitosamente"
        return False, "Error al desactivar usuario"
    except Exception as e:
        return False, f"Error: {str(e)}"

def reactivar_usuario(id_usuario):
    """Re-activa un usuario desactivado"""
    try:
        result = supabase.table("usuarios").update({"activo": True}).eq("id_usuario", id_usuario).execute()
        if result.data:
            return True, "Usuario reactivado exitosamente"
        return False, "Error al reactivar usuario"
    except Exception as e:
        return False, f"Error: {str(e)}"

def resetear_password(id_usuario, nueva_password):
    """Resetea la contraseña de un usuario"""
    if not nueva_password or len(nueva_password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres"
    
    try:
        password_hash = hash_password(nueva_password)
        result = supabase.table("usuarios").update({"password_hash": password_hash}).eq("id_usuario", id_usuario).execute()
        if result.data:
            return True, "Contraseña actualizada exitosamente"
        return False, "Error al actualizar contraseña"
    except Exception as e:
        return False, f"Error: {str(e)}"

def actualizar_mi_perfil(id_usuario, nombres, apellidos, correo):
    """Actualiza los datos del perfil del usuario actual (sin cambiar DNI)"""
    if not nombres or not apellidos:
        return False, "Nombres y apellidos son obligatorios"
    
    valido, mensaje = validar_correo(correo)
    if not valido:
        return False, mensaje
    
    nombres_limpio = limpiar_nombre(nombres)
    apellidos_limpio = limpiar_nombre(apellidos)
    correo_limpio = correo.strip().lower()
    
    # Verificar si el correo ya existe en otro usuario
    existe_correo = supabase.table("usuarios").select("id_usuario").eq("correo", correo_limpio).neq("id_usuario", id_usuario).execute()
    if existe_correo.data:
        return False, f"Ya existe otro usuario con correo {correo_limpio}"
    
    try:
        result = supabase.table("usuarios").update({
            "nombres": nombres_limpio,
            "apellidos": apellidos_limpio,
            "correo": correo_limpio,
            "actualizado_en": datetime.now().isoformat()
        }).eq("id_usuario", id_usuario).execute()
        
        if result.data:
            return True, "Perfil actualizado exitosamente"
        return False, "Error al actualizar perfil"
    except Exception as e:
        return False, f"Error: {str(e)}"

# ============================================
# FUNCIONES CRUD PARA EQUIPOS
# ============================================

def listar_equipos():
    """Obtiene lista de todos los equipos"""
    try:
        response = supabase.table("equipos").select("*").order("creado_en", desc=True).limit(100).execute()
        return response.data if response.data else []
    except:
        return []

def crear_equipo(datos):
    """Crea un nuevo equipo"""
    try:
        result = supabase.table("equipos").insert(datos).execute()
        if result.data:
            return True, "Equipo agregado exitosamente"
        return False, "Error al agregar equipo"
    except Exception as e:
        return False, f"Error: {str(e)}"

def obtener_marcas():
    """Obtiene lista de marcas"""
    try:
        response = supabase.table("marcas").select("id_marca, descripcion").eq("activo", True).execute()
        if response.data:
            return {m["descripcion"]: m["id_marca"] for m in response.data}
        return {"HP": 1, "Lenovo": 2, "Dell": 3, "Apple": 4, "Samsung": 5, "Epson": 6}
    except:
        return {"HP": 1, "Lenovo": 2, "Dell": 3, "Apple": 4, "Samsung": 5, "Epson": 6}

def obtener_tipos_equipo():
    """Obtiene lista de tipos de equipo activos para usar en formularios"""
    try:
        response = supabase.table("tipo_equipos").select("id_tipo, descripcion").eq("activo", True).execute()
        if response.data:
            return {t["descripcion"]: t["id_tipo"] for t in response.data}
        return {"Laptop": 1, "Desktop": 2, "Tablet": 3, "Proyector": 4, "Monitor": 5, "Impresora": 6}
    except:
        return {"Laptop": 1, "Desktop": 2, "Tablet": 3, "Proyector": 4, "Monitor": 5, "Impresora": 6}

# ============================================
# FUNCIÓN DE LOGIN
# ============================================

def check_login(dni, password):
    """Verifica las credenciales del usuario"""
    hashed_pass = hash_password(password)
    try:
        response = supabase.table("usuarios").select("*").eq("dni", dni).eq("password_hash", hashed_pass).eq("activo", True).execute()
        if response.data:
            user = response.data[0]
            # Actualizar último login
            supabase.table("usuarios").update({"ultimo_login": datetime.now().isoformat()}).eq("id_usuario", user["id_usuario"]).execute()
            return user
        return None
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# ============================================
# CONFIGURACIÓN DE PÁGINA Y ESTADO
# ============================================

st.set_page_config(page_title="Sistema de Inventario - Colegio", page_icon="📚", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ============================================
# LOGIN
# ============================================

if not st.session_state.logged_in:
    st.title("📋 Sistema de Gestión de Inventario")
    st.markdown("---")
    st.subheader("🔐 Inicio de Sesión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        dni_input = st.text_input("📇 DNI (8 dígitos)", max_chars=8, placeholder="Ej: 12345678")
        password_input = st.text_input("🔒 Contraseña", type="password", placeholder="••••••")
        
        if st.button("🚪 Ingresar", type="primary", use_container_width=True):
            if dni_input and password_input:
                user_data = check_login(dni_input, password_input)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.success(f"✅ ¡Bienvenido/a {user_data['nombres']}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.warning("⚠️ Por favor ingresa tu DNI y contraseña")

# ============================================
# MENÚ PRINCIPAL
# ============================================

else:
    user = st.session_state.user
    perfiles_dict = obtener_perfiles()
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.markdown(f"### 👤 {user['nombres']} {user['apellidos']}")
        st.markdown(f"**📧 {user['correo']}**")
        st.markdown(f"**🆔 DNI:** {user['dni']}")
        st.markdown(f"**⭐ Perfil:** {obtener_perfil_nombre(user['id_perfil'])}")
        st.markdown("---")
        
        menu = st.radio(
            "📌 Menú",
            ["📊 Dashboard", "🖥️ Equipos", "➕ Nuevo Equipo", "📦 Tipos de Equipo", "👥 Usuarios", "➕ Agregar Usuario", "📈 Reportes", "👤 Mi Perfil"],
            index=0
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # ============================================
    # DASHBOARD
    # ============================================
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            equipos_count = supabase.table("equipos").select("*", count="exact").execute()
            total_equipos = equipos_count.count if equipos_count.count else 0
            
            usuarios_count = supabase.table("usuarios").select("*", count="exact").eq("activo", True).execute()
            total_usuarios = usuarios_count.count if usuarios_count.count else 0
            
            ubicaciones_count = supabase.table("ubicaciones").select("*", count="exact").execute()
            total_ubicaciones = ubicaciones_count.count if ubicaciones_count.count else 0
            
            tipos_count = supabase.table("tipo_equipos").select("*", count="exact").execute()
            total_tipos = tipos_count.count if tipos_count.count else 0
        except:
            total_equipos = 0
            total_usuarios = 0
            total_ubicaciones = 0
            total_tipos = 0
        
        col1.metric("🖥️ Total Equipos", total_equipos)
        col2.metric("👥 Usuarios Activos", total_usuarios)
        col3.metric("📍 Ubicaciones", total_ubicaciones)
        col4.metric("📂 Tipos de Equipo", total_tipos)
        
        st.info("💡 Bienvenido al sistema de inventario. Usa el menú lateral para navegar.")
    
    # ============================================
    # LISTAR EQUIPOS
    # ============================================
    elif menu == "🖥️ Equipos":
        st.header("📋 Listado de Equipos")
        with st.spinner("Cargando equipos..."):
            equipos = listar_equipos()
            if equipos:
                df = pd.DataFrame(equipos)
                columnas_mostrar = ["codigo_patrimonial", "modelo", "numero_serie", "anio_compra"]
                df_mostrar = df[[c for c in columnas_mostrar if c in df.columns]]
                st.dataframe(df_mostrar, use_container_width=True)
            else:
                st.warning("No hay equipos registrados. Usa 'Nuevo Equipo' para agregar.")
    
    # ============================================
    # NUEVO EQUIPO
    # ============================================
    elif menu == "➕ Nuevo Equipo":
        st.header("➕ Registrar Nuevo Equipo")
        
        marcas_dict = obtener_marcas()
        tipos_dict = obtener_tipos_equipo()
        
        with st.form("form_equipo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                codigo_pat = st.text_input("📝 Código Patrimonial*")
                modelo = st.text_input("🏷️ Modelo*")
                numero_serie = st.text_input("🔢 Número de Serie")
                marca = st.selectbox("🏭 Marca", list(marcas_dict.keys()))
                anio_compra = st.number_input("📅 Año de Compra", min_value=1990, max_value=2025, step=1)
            with col2:
                tipo = st.selectbox("📂 Tipo de Equipo", list(tipos_dict.keys()))
                proveedor = st.text_input("🏢 Proveedor")
                costo = st.number_input("💰 Costo de Compra", min_value=0.0, step=100.0)
                garantia = st.date_input("📅 Garantía hasta", value=None)
            
            observacion = st.text_area("📝 Observaciones", placeholder="Detalles adicionales...")
            
            submitted = st.form_submit_button("💾 Guardar Equipo", type="primary", use_container_width=True)
            
            if submitted:
                if codigo_pat and modelo:
                    nuevo_equipo = {
                        "codigo_patrimonial": codigo_pat,
                        "modelo": modelo,
                        "numero_serie": numero_serie if numero_serie else None,
                        "id_marca": marcas_dict[marca],
                        "id_tipo": tipos_dict[tipo],
                        "anio_compra": anio_compra,
                        "proveedor": proveedor if proveedor else None,
                        "costo_compra": costo if costo > 0 else None,
                        "garantia_hasta": garantia.isoformat() if garantia else None,
                        "observacion_general": observacion if observacion else None,
                        "activo": True
                    }
                    ok, mensaje = crear_equipo(nuevo_equipo)
                    if ok:
                        st.success(mensaje)
                        st.balloons()
                    else:
                        st.error(mensaje)
                else:
                    st.warning("⚠️ El código patrimonial y modelo son obligatorios")
    
    # ============================================
    # TIPOS DE EQUIPO - CRUD COMPLETO (CORREGIDO)
    # ============================================
    elif menu == "📦 Tipos de Equipo":
        st.header("📦 Gestión de Tipos de Equipo")
        st.markdown("---")
        
        # Botones de acción
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("🔄 Recargar Listado", use_container_width=True):
                st.rerun()
        with col_btn2:
            if st.button("📦 Insertar Tipos por Defecto", use_container_width=True):
                tipos_default = [
                    ("Laptop", "Computadora", 5),
                    ("Desktop", "Computadora", 5),
                    ("Tablet", "Computadora", 4),
                    ("Proyector", "Multimedia", 5),
                    ("Monitor", "Periférico", 5),
                    ("Impresora", "Periférico", 4),
                    ("Router", "Red", 5),
                    ("Switch", "Red", 5),
                    ("Servidor", "Infraestructura", 7),
                ]
                for desc, cat, vida in tipos_default:
                    ok, msg = crear_tipo_equipo(desc, cat, vida)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                st.rerun()
        
        st.markdown("---")
        
        # Formulario para agregar
        with st.expander("➕ Agregar Nuevo Tipo de Equipo", expanded=False):
            with st.form("form_tipo_equipo", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    descripcion = st.text_input("📝 Descripción*", placeholder="Ej: Laptop")
                    categoria = st.text_input("📂 Categoría*", placeholder="Ej: Computadora")
                with col2:
                    vida_util = st.number_input("⏱️ Vida Útil (años)*", min_value=1, max_value=20, step=1, value=5)
                
                submitted = st.form_submit_button("💾 Guardar Tipo de Equipo", type="primary", use_container_width=True)
                
                if submitted:
                    if not descripcion:
                        st.error("❌ La descripción es obligatoria")
                    elif not categoria:
                        st.error("❌ La categoría es obligatoria")
                    else:
                        ok, mensaje = crear_tipo_equipo(descripcion, categoria, vida_util)
                        if ok:
                            st.success(f"✅ {mensaje}")
                            st.rerun()
                        else:
                            st.error(f"❌ {mensaje}")
        
        st.markdown("---")
        st.subheader("📋 Listado de Tipos de Equipo")
        
        # Obtener y mostrar tipos
        tipos = listar_tipos_equipos()
        
        if tipos and len(tipos) > 0:
            st.success(f"✅ Se encontraron {len(tipos)} tipos de equipo")
            for tipo in tipos:
                estado_texto = "🟢 Activo" if tipo.get('activo', True) else "🔴 Inactivo"
                with st.expander(f"📌 {tipo['descripcion']} - {tipo['categoria']} ({estado_texto})"):
                    with st.form(key=f"edit_tipo_{tipo['id_tipo']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_descripcion = st.text_input("Descripción", value=tipo['descripcion'], key=f"desc_{tipo['id_tipo']}")
                            edit_categoria = st.text_input("Categoría", value=tipo['categoria'], key=f"cat_{tipo['id_tipo']}")
                        with col2:
                            edit_vida_util = st.number_input("Vida Útil (años)", value=tipo.get('vida_util_anios', 5), min_value=1, max_value=20, step=1, key=f"vida_{tipo['id_tipo']}")
                            edit_activo = st.checkbox("Activo", value=tipo.get('activo', True), key=f"act_{tipo['id_tipo']}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                                if edit_descripcion and edit_categoria:
                                    ok, msg = actualizar_tipo_equipo(tipo['id_tipo'], edit_descripcion, edit_categoria, edit_vida_util, edit_activo)
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                else:
                                    st.warning("La descripción y categoría son obligatorias")
                        
                        with col_btn2:
                            if tipo.get('activo', True):
                                if st.form_submit_button("🔴 Desactivar", type="secondary"):
                                    ok, msg = eliminar_tipo_equipo(tipo['id_tipo'])
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            else:
                                if st.form_submit_button("🟢 Reactivar", type="secondary"):
                                    ok, msg = reactivar_tipo_equipo(tipo['id_tipo'])
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                        
                        st.markdown(f"**🆔 ID:** {tipo['id_tipo']} | **📅 Creado:** {tipo.get('creado_en', 'N/A')[:10] if tipo.get('creado_en') else 'N/A'}")
        else:
            st.warning("⚠️ No hay tipos de equipo registrados.")
            st.info("💡 Usa el botón '📦 Insertar Tipos por Defecto' para cargar los tipos básicos, o agrega uno manualmente con el formulario arriba.")
    
    # ============================================
    # LISTAR USUARIOS
    # ============================================
    elif menu == "👥 Usuarios":
        st.header("👥 Gestión de Usuarios")
        
        usuarios = listar_usuarios()
        
        if usuarios:
            for u in usuarios:
                es_usuario_actual = (u['id_usuario'] == user['id_usuario'])
                
                with st.expander(f"📌 {u['nombres']} {u['apellidos']} - {u['dni']}"):
                    with st.form(key=f"edit_form_{u['id_usuario']}"):
                        st.markdown("### ✏️ Editar Datos Personales")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            nuevo_dni = st.text_input("DNI", value=u['dni'], max_chars=8, key=f"dni_{u['id_usuario']}", disabled=es_usuario_actual)
                            nuevos_nombres = st.text_input("Nombres", value=u['nombres'], key=f"nombres_{u['id_usuario']}")
                            nuevos_apellidos = st.text_input("Apellidos", value=u['apellidos'], key=f"apellidos_{u['id_usuario']}")
                        with col2:
                            nuevo_correo = st.text_input("Correo", value=u['correo'], key=f"correo_{u['id_usuario']}")
                            perfil_actual = obtener_perfil_nombre(u['id_perfil'])
                            perfiles_nombres = list(perfiles_dict.keys())
                            idx_actual = perfiles_nombres.index(perfil_actual) if perfil_actual in perfiles_nombres else 0
                            nuevo_perfil = st.selectbox("Perfil", perfiles_nombres, index=idx_actual, key=f"perfil_select_{u['id_usuario']}")
                        
                        if not es_usuario_actual:
                            if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                                if nuevo_dni and nuevos_nombres and nuevos_apellidos and nuevo_correo:
                                    nuevo_id_perfil = perfiles_dict[nuevo_perfil]
                                    ok, msg = actualizar_datos_usuario(
                                        u['id_usuario'], nuevo_dni, nuevos_nombres, 
                                        nuevos_apellidos, nuevo_correo, nuevo_id_perfil
                                    )
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                else:
                                    st.warning("Todos los campos son obligatorios")
                        else:
                            st.info("ℹ️ No puedes editar tus propios datos aquí. Ve a 'Mi Perfil' para hacerlo.")
                    
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        if u['activo']:
                            if st.button(f"🔴 Desactivar", key=f"des_{u['id_usuario']}"):
                                ok, msg = eliminar_usuario(u['id_usuario'])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        else:
                            if st.button(f"🟢 Reactivar", key=f"act_{u['id_usuario']}"):
                                ok, msg = reactivar_usuario(u['id_usuario'])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    
                    with col2:
                        with st.popover("🔑 Resetear Contraseña"):
                            nueva_pass = st.text_input("Nueva contraseña", type="password", key=f"pass_input_{u['id_usuario']}")
                            if st.button(f"Aplicar", key=f"reset_{u['id_usuario']}"):
                                if nueva_pass and len(nueva_pass) >= 4:
                                    ok, msg = resetear_password(u['id_usuario'], nueva_pass)
                                    if ok:
                                        st.success(msg)
                                    else:
                                        st.error(msg)
                                else:
                                    st.warning("Mínimo 4 caracteres")
                    
                    with col3:
                        st.markdown(f"**📅 Creado:** {u.get('creado_en', 'N/A')[:10] if u.get('creado_en') else 'N/A'}")
                        st.markdown(f"**🟢 Estado:** {'✅ Activo' if u['activo'] else '❌ Inactivo'}")
        else:
            st.info("No hay usuarios registrados")
    
    # ============================================
    # AGREGAR USUARIO
    # ============================================
    elif menu == "➕ Agregar Usuario":
        st.header("➕ Agregar Nuevo Usuario")
        st.markdown("---")
        
        perfiles_nombres = list(perfiles_dict.keys())
        
        with st.form("form_usuario", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                dni = st.text_input("📇 DNI (8 dígitos, solo números)*", max_chars=8, 
                                   placeholder="Ej: 12345678",
                                   help="Debe tener exactamente 8 dígitos numéricos")
                nombres = st.text_input("📝 Nombres*", placeholder="Ej: juan carlos")
                apellidos = st.text_input("📝 Apellidos*", placeholder="Ej: perez gonzalez")
            with col2:
                correo = st.text_input("📧 Correo Electrónico*", placeholder="Ej: usuario@colegio.edu")
                password = st.text_input("🔒 Contraseña*", type="password", placeholder="Mínimo 4 caracteres")
                perfil = st.selectbox("⭐ Perfil de Usuario*", perfiles_nombres)
            
            submitted = st.form_submit_button("💾 Crear Usuario", type="primary", use_container_width=True)
            
            if submitted:
                if not dni:
                    st.error("❌ El DNI es obligatorio")
                elif not nombres:
                    st.error("❌ Los nombres son obligatorios")
                elif not apellidos:
                    st.error("❌ Los apellidos son obligatorios")
                elif not correo:
                    st.error("❌ El correo es obligatorio")
                elif not password:
                    st.error("❌ La contraseña es obligatoria")
                else:
                    id_perfil = perfiles_dict[perfil]
                    ok, mensaje = crear_usuario(dni, nombres, apellidos, correo, password, id_perfil)
                    if ok:
                        st.success(f"✅ {mensaje}")
                        st.balloons()
                    else:
                        st.error(f"❌ {mensaje}")
        
        st.markdown("---")
        st.subheader("📋 Usuarios Registrados Recientemente")
        usuarios = listar_usuarios()
        if usuarios:
            df_usuarios = pd.DataFrame(usuarios[:5])
            columnas = ["dni", "nombres", "apellidos", "correo", "activo"]
            df_mostrar = df_usuarios[[c for c in columnas if c in df_usuarios.columns]]
            st.dataframe(df_mostrar, use_container_width=True)
        else:
            st.info("No hay usuarios registrados aún")
    
    # ============================================
    # REPORTES
    # ============================================
    elif menu == "📈 Reportes":
        st.header("📊 Reportes y Estadísticas")
        st.info("🚧 Módulo en construcción. Próximamente: reportes por año, ubicación, estado, etc.")
    
    # ============================================
    # MI PERFIL
    # ============================================
    elif menu == "👤 Mi Perfil":
        st.header("👤 Mi Perfil")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📋 Información Actual")
            st.markdown(f"**Nombre:** {user['nombres']}")
            st.markdown(f"**Apellidos:** {user['apellidos']}")
            st.markdown(f"**DNI:** {user['dni']} (No modificable)")
            st.markdown(f"**Correo:** {user['correo']}")
        with col2:
            st.markdown("### 🔐 Información de Sesión")
            st.markdown(f"**Último acceso:** {user.get('ultimo_login', 'Nunca')}")
            st.markdown(f"**Perfil:** {obtener_perfil_nombre(user['id_perfil'])}")
            st.markdown(f"**Estado:** {'✅ Activo' if user['activo'] else '❌ Inactivo'}")
        
        st.markdown("---")
        
        st.subheader("✏️ Editar Mis Datos")
        with st.form("editar_mi_perfil"):
            col1, col2 = st.columns(2)
            with col1:
                nuevos_nombres = st.text_input("Nombres", value=user['nombres'])
                nuevos_apellidos = st.text_input("Apellidos", value=user['apellidos'])
            with col2:
                nuevo_correo = st.text_input("Correo Electrónico", value=user['correo'])
            
            submitted_edit = st.form_submit_button("💾 Actualizar Mis Datos", type="primary", use_container_width=True)
            
            if submitted_edit:
                if nuevos_nombres and nuevos_apellidos and nuevo_correo:
                    ok, msg = actualizar_mi_perfil(user['id_usuario'], nuevos_nombres, nuevos_apellidos, nuevo_correo)
                    if ok:
                        st.success(msg)
                        user['nombres'] = limpiar_nombre(nuevos_nombres)
                        user['apellidos'] = limpiar_nombre(nuevos_apellidos)
                        user['correo'] = nuevo_correo.strip().lower()
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Todos los campos son obligatorios")
        
        st.markdown("---")
        
        st.subheader("🔑 Cambiar Contraseña")
        with st.form("cambiar_password"):
            col1, col2 = st.columns(2)
            with col1:
                nueva_pass = st.text_input("Nueva Contraseña", type="password")
            with col2:
                confirmar_pass = st.text_input("Confirmar Contraseña", type="password")
            
            if st.form_submit_button("🔄 Actualizar Contraseña", use_container_width=True):
                if not nueva_pass:
                    st.error("Ingresa una nueva contraseña")
                elif len(nueva_pass) < 4:
                    st.error("La contraseña debe tener al menos 4 caracteres")
                elif nueva_pass != confirmar_pass:
                    st.error("Las contraseñas no coinciden")
                else:
                    ok, msg = resetear_password(user['id_usuario'], nueva_pass)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)