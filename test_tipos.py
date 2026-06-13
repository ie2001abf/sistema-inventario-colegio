from supabase import create_client

# CONFIGURACIÓN DE SUPABASE
SUPABASE_URL = "https://cbwapocafiigqxbxpfok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNid2Fwb2NhZmlpZ3F4YnhwZm9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODUyNTcsImV4cCI6MjA5Njc2MTI1N30.Xzc_rB6tfx4j6A9nlBQgRoD-Wu8Tuz3VlYTRUsnPFhQ"

print("🔍 Inicializando cliente de Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Cliente creado")

print("\n🔍 Consultando tabla tipo_equipos...")

try:
    response = supabase.table("tipo_equipos").select("*").execute()
    print(f"✅ Conexión exitosa")
    print(f"📊 Tipos de equipo encontrados: {len(response.data) if response.data else 0}")
    
    if response.data:
        print("\n📋 Listado de tipos:")
        for tipo in response.data:
            print(f"   - ID: {tipo['id_tipo']} | {tipo['descripcion']} | {tipo['categoria']} | Activo: {tipo['activo']}")
    else:
        print("\n⚠️ No hay tipos de equipo registrados en la base de datos")
        print("💡 Ejecuta el SQL en Supabase para insertar los tipos")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Tipo de error: {type(e).__name__}")

print("\n🔍 Probando conexión básica...")
try:
    test_response = supabase.table("usuarios").select("count").execute()
    print("✅ Conexión a tabla usuarios OK")
except Exception as e:
    print(f"❌ Error en tabla usuarios: {e}")