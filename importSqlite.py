import sqlite3
import csv

with open('./members.csv', newline='') as f:
    csv_reader = csv.DictReader(f)
    members = [(row['name'], row['group']) for row in csv_reader ]

print(members)

with open('create_db.sql') as f:
    create_db_sql = f.read()

db = sqlite3.connect('members.db')
with db:
    db.executescript(create_db_sql)

with db:
    db.executemany('INSERT INTO  members (name, group_name) VALUES (?,?)',members )


c = db.execute('SELECT * FROM members LIMIT 3')
for row in c:
    print(row)
