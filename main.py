from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection
try:
    # Test with the correct table name 'User' (capital U)
    result = supabase.table('User').select('*').limit(1).execute()
    print("Connection successful!")
    print("Sample query result:", result.data)

except Exception as e:
    print(f"Failed to connect: {e}")