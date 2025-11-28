"""
Check actual database columns
"""
import sqlite3

conn = sqlite3.connect('tevkil.db')
cursor = conn.cursor()

print("=== USERS TABLOSU KOLONLARI ===\n")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

for col in columns:
    print(f"ID: {col[0]}, Name: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}, PK: {col[5]}")

print(f"\nToplam {len(columns)} kolon bulundu")

# Check if specific columns exist
required_columns = ['tc_number', 'bar_association', 'bar_registration_number', 
                   'attended_hearings_count', 'completed_tasks_count']

existing = [col[1] for col in columns]
print("\n=== KONTROL EDİLEN KOLONLAR ===")
for req_col in required_columns:
    status = "✅ VAR" if req_col in existing else "❌ YOK"
    print(f"{status}: {req_col}")

conn.close()
