from .database import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    uid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    uname = db.Column(db.String(255), unique=True, nullable=False)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    pro_pic = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.String(255))
    pwd = db.Column(db.String(255), nullable=False)
    posts = db.relationship('Post', backref='user')
    comments = db.relationship('Comment', backref='user')
    followings = db.relationship('Following', backref='user')
    followers = db.relationship('Follower', backref='user')
    likes = db.relationship('Like', backref='user')

    def __init__(self, uname, fname, lname, email, pwd):
        self.uname = uname
        self.fname = fname
        self.lname = lname
        self.email = email
        self.pro_pic = "user-big.png"
        self.bio = "Blogging is cool!"
        self.pwd = pwd

    def get_id(self):
        return self.uid

    def following(self, user):
        for u in self.followings:
            if u.fid == user.uid:
                return True
        return False


class Post(db.Model):
    __tablename__ = 'post'
    pid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
    images = db.relationship('Image', backref='post')
    comments = db.relationship('Comment', backref='post')
    likes = db.relationship('Like', backref='post')

    def __init__(self, title, description, timestamp, uid):
        self.title = title
        self.description = description
        self.timestamp = timestamp
        self.uid = uid


class Comment(db.Model):
    __tablename__ = 'comment'
    cid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey('post.pid'), nullable=False)

    def __init__(self, content, timestamp, uid, pid):
        self.content = content
        self.timestamp = timestamp
        self.uid = uid
        self.pid = pid


class Image(db.Model):
    __tablename__ = 'image'
    iid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey('post.pid'), nullable=False)

    def __init__(self, url, pid):
        self.url = url
        self.pid = pid


class Following(db.Model):
    __tablename__ = 'following'
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    fid = db.Column(db.Integer, primary_key=True)

    def __init__(self, uid, fid):
        self.uid = uid
        self.fid = fid


class Follower(db.Model):
    __tablename__ = 'follower'
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    fid = db.Column(db.Integer, primary_key=True)

    def __init__(self, uid, fid):
        self.uid = uid
        self.fid = fid


class Like(db.Model):
    __tablename__ = 'like'
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('post.pid'), primary_key=True)

    def __init__(self, uid, pid):
        self.uid = uid
        self.pid = pid
