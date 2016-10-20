import random
import csv
import sqlite3
from flask import Flask, render_template, request, g, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

GROUPS = ['General', 'Expensive', 'Taste', 'Cheap']

app = Flask(__name__)
app.config['SECRET_KEY'] = "random string"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'

db = SQLAlchemy(app)


@app.route('/')
def hello():
    for val in GROUPS:
        print(val)
    return "<p>Hello World!</p>"


@app.route('/test1')
def index():
    return render_template('index.html')


class members(db.Model):
    __tablename__ = 'members'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    group_name = db.Column(db.String(50))


def __init__(self, name, group_name):
    self.name = name
    self.group_name = group_name


@app.route('/showAll', methods=['GET', 'POST'])
def show_all():
    selectGroup_name = request.form.get('select_group_name')

    if selectGroup_name == 'ALL' or selectGroup_name is None:
        selectMembers = members.query.all()
        count = members.query.count()
    else:
        selectMembers = members.query.filter_by(
            group_name=selectGroup_name).all()
        count = members.query.filter_by(group_name=selectGroup_name).count()

    myGroups = []
    for g in GROUPS:
        myGroups.append(g)
    myGroups.append('ALL')

    return render_template('show_all.html',
                           members=selectMembers,
                           groups=myGroups,
                           total=count)


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['group_name']:
            flash('Please enter all the fields', 'error')
        else:
            print(request.form.get('name'), '+',
                  request.form.get('group_name'))
            member = members(
                name=request.form['name'],
                group_name=request.form['group_name'])

            db.session.add(member)
            db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html', groups=GROUPS)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    memberList = members.query.all()
    myfoodList = ['none']
    for g in memberList:
        myfoodList.append(g.name)

    if request.method == 'POST':
        print('you select ', request.form.get('select_name'))
        if request.form.get('select_name') == 'none':
            flash('Please enter all the fields', 'error')
        else:

            member = members.query.filter_by(
                name=request.form.get('select_name'))
            # print( member[0].name, '+', member[0].group_name)

            # two way to delete record
            # db.session.query(members).filter(members.name == member[0].name).delete()
            db.session.query(members).filter_by(name=member[0].name).delete()

            db.session.commit()

            outputMsg = request.form.get(
                'select_name') + ' was successfully deleted'
            flash(outputMsg)
            return redirect(url_for('show_all'))
    return render_template('delete.html', foodList=myfoodList)


@app.route('/update', methods=['GET', 'POST'])
def update():
    print('update function')
    memberList = members.query.all()
    myfoodList = []
    for g in memberList:
        myfoodList.append(g.name)

    if request.method == 'POST':
        print('you select food is ', request.form.get('select_name'),
              ', group is ', request.form.get('group_name'))
        if request.form.get('select_name') == 'none':
            flash('Please enter all the fields', 'error')
        else:

            member = members.query.filter_by(
                name=request.form.get('select_name'))
            # print( member[0].name, '+', member[0].group_name)

            # db.session.query(members).filter(members.name == member[0].name).update({'group_name': request.form.get('group_name')})
            db.session.query(members).filter_by(name=member[0].name).update(
                {"group_name": request.form.get('group_name')})
            db.session.commit()

            outputMsg = request.form.get('select_name')
            + ' was successfully update group to ['
            + request.form.get('group_name')
            + ']'

            flash(outputMsg)
            return redirect(url_for('show_all'))
    return render_template('update.html',
                           groups=GROUPS,
                           foodList=myfoodList)

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

    # return '<p>%s(group：%s)</p>' % (member_name, member_group_name)

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
