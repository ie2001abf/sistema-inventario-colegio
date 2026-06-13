from supabase import create_client

# Reemplaza con TUS datos nuevos
URL = "https://cbwapocafiigqxbxpfok.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNid2Fwb2NhZmlpZ3F4YnhwZm9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExODUyNTcsImV4cCI6MjA5Njc2MTI1N30.Xzc_rB6tfx4j6A9nlBQgRoD-Wu8Tuz3VlYTRUsnPFhQ"

try:
    supabase = create_client(URL, KEY)
    result = supabase.table("usuarios").select("count").execute()
    print("✅ Conexión exitosa!")
    print(f"   Usuarios encontrados: {result.count}")
except Exception as e:
    print(f"❌ Error: {e}")