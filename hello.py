import random
import csv
import sqlite3
from flask import Flask, render_template, request, g
app = Flask(__name__)

@app.route('/')
def hello():
    return "<p>Hello World!</p>"


@app.route('/test')
def test():
    return "<p>Henry Test!</p>"
	
@app.route('/test1')
def index():
    return render_template('index.html')
	
SQLITE_DB_PATH = 'members.db'
SQLITE_DB_SCHEMA = 'create_db.sql'
MEMBER_CSV_PATH = 'members.csv'


# SQLite3-related operations
# See SQLite3 usage pattern from Flask official doc
# http://flask.pocoo.org/docs/0.10/patterns/sqlite3/
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
	
	
@app.route('/draw', methods=['POST'])
def draw():
    # Get the database connection
    db = get_db()

    # Draw member ids from given group
    # If ALL is given then draw from all members
    group_name = request.form.get('group_name', 'ALL')
    valid_members_sql = 'SELECT id FROM members '
    if group_name == 'ALL':
        cursor = db.execute(valid_members_sql)
    else:
        valid_members_sql += 'WHERE group_name = ?'
        cursor = db.execute(valid_members_sql, (group_name, ))
    valid_member_ids = [
        row[0] for row in cursor
    ]

    # If no valid members return 404 (unlikely)
    if not valid_member_ids:
        err_msg = "<p>No members in group '%s'</p>" % group_name
        return err_msg, 404

    # Randomly choice a member
    lucky_member_id = random.choice(valid_member_ids)

    # Obtain the lucy member's information
    member_name, member_group_name = db.execute(
        'SELECT name, group_name FROM members WHERE id = ?',
        (lucky_member_id, )
    ).fetchone()
	
	# Update draw history
    with db:
        db.execute('INSERT INTO draw_histories (memberid) VALUES (?)',
                   (lucky_member_id, ))

    #return '<p>%s(group：%s)</p>' % (member_name, member_group_name)
	
    return render_template(
	    'draw.html',
	    name=member_name,
	    group=member_group_name,
	)

@app.route('/history')
def history():
    db = get_db()
    recent_histories = db.execute(
        'SELECT m.name, m.group_name, d.time '
        'FROM draw_histories AS d, members as m '
        'WHERE m.id == d.memberid '
        'ORDER BY d.time DESC '
        'LIMIT 10'
    ).fetchall()
    return render_template(
        'history.html',
        recent_histories=recent_histories
    )


@app.route('/reset')
def reset_db():
    with open(SQLITE_DB_SCHEMA, 'r') as f:
        create_db_sql = f.read()
    db = get_db()
    # Reset database
    # Note that CREATE/DROP table are *immediately* committed
    # even inside a transaction
    with db:
        db.execute("DROP TABLE IF EXISTS draw_histories")
        db.execute("DROP TABLE IF EXISTS members")
        db.executescript(create_db_sql)

    # Read members CSV data
    with open(MEMBER_CSV_PATH, newline='') as f:
        csv_reader = csv.DictReader(f)
        members = [
            (row['name'], row['group'])
            for row in csv_reader
        ]

    # Write members into database
    with db:
        db.executemany(
            'INSERT INTO members (name, group_name) VALUES (?, ?)',
            members
        )
    return render_template(
	    'index.html'
	)
	
	
if __name__ == '__main__':
    app.run(debug=True)