import sqlite3

conn = sqlite3.connect('black2.db')
cursor = conn.cursor()

# Query users with referral info
cursor.execute('SELECT address, email, tu1, tu2, tu3 FROM users')
rows = cursor.fetchall()

print(f"Total users: {len(rows)}")
print("\nAddress | Email | TU1 | TU2 | TU3")
print("-" * 80)
for r in rows:
    addr = r[0][:12] + "..." if r[0] else ""
    email = r[1]
    tu1 = r[2][:12] + "..." if r[2] else "None"
    tu2 = r[3][:12] + "..." if r[3] else "None"
    tu3 = r[4][:12] + "..." if r[4] else "None"
    print(f"{addr} | {email} | {tu1} | {tu2} | {tu3}")

# Check transaction_referrals
print("\n\nTransaction Referrals:")
cursor.execute('SELECT tx_id, tu1_address, tu1_amount, tu2_address, tu2_amount, tu3_address, tu3_amount, settlement_status FROM transaction_referrals')
ref_rows = cursor.fetchall()
for r in ref_rows:
    print(f"TX: {r[0][:12]}... | TU1: {r[1][:12] if r[1] else 'None'} ({r[2]}) | TU2: {r[3][:12] if r[3] else 'None'} ({r[4]}) | TU3: {r[5][:12] if r[5] else 'None'} ({r[6]}) | Status: {r[7]}")

conn.close()
