print("Script started")

from database import engine
from sqlalchemy import text

print("About to connect...")

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connected successfully:", result.fetchone())

print("Script finished")