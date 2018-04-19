# Microsoft sql
import pymssql

conn = pymssql.connect(server=server, user=user, password=password, database=db)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(MemberID) as count FROM Members WHERE id = 1")
row = cursor.fetchone()

conn.close()

print(row)