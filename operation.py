from hello import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app.config['SECRET_KEY'] = "random string"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///members.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://snake_eyes:123456@140.96.29.153/MyTest'

#db = SQLAlchemy(app)

db = SQLAlchemy(app)


class members(db.Model):
    __tablename__ = 'members'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    group_name = db.Column(db.String(50))


    def __init__(self, name, group_name):
        self.name = name
        self.group_name = group_name

class draw_histories(db.Model):
    __tablename__ = 'draw_histories'
    draw_histories_id = db.Column('draw_histories_id', db.Integer, primary_key=True)
    memberid = db.Column(db.Integer, db.ForeignKey('members.id'))
    time = db.Column(db.DATETIME, default=datetime.now)
    member = db.relationship('members', foreign_keys=memberid)

def showData(selectGroup_name):
    if selectGroup_name == 'ALL' or selectGroup_name is None:
        selectMembers = members.query.all()
    else:
        selectMembers = members.query.filter_by(
            group_name=selectGroup_name).all()

    return selectMembers


def addData(n, g_name):
    if n is not None or g_name is not None:
        member = members(name=n, group_name=g_name)
        print(member.name, '+', member.group_name)
        db.session.add(member)
        db.session.commit()


def deleteData(select_name):
    member = members.query.filter_by(name=select_name)
    #print(member[0].name, '+', member[0].group_name)

    # two way to delete record
    # db.session.query(members).filter(members.name == member[0].name).delete()
    db.session.query(members).filter_by(name=member[0].name).delete()
    db.session.commit()


def updateData(n, g_name):
    member = members.query.filter_by(name=n)
    # print( member[0].name, '+', member[0].group_name)

    # db.session.query(members).filter(members.name == member[0].name).update({'group_name': request.form.get('group_name')})
    db.session.query(members).filter_by(name=member[0].name).update({"group_name": g_name})
    db.session.commit()

def showHistories():
    histories = draw_histories.query.all()

    return histories

def getDataById(mId):
    if mId == 'ALL' or mId is None:
        selectMembers = members.query.all()
    else:
        selectMembers = members.query.filter_by(
            id=mId).all()

    return selectMembers

def addHistory(m):
    if m is not None:
        print(m[0].id)
        drawHistory = draw_histories(memberid=m[0].id)
        #print(drawHistory.member.name, '+', drawHistory.member.group_name)
        db.session.add(drawHistory)
        db.session.commit()
