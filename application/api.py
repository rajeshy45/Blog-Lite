from flask_restful import Resource, fields, marshal_with, reqparse
from application.database import db
from application.models import *
from application.validation import *
from datetime import datetime

user_output_fields = {
    "uid": fields.Integer,
    "uname": fields.String,
    "fname": fields.String,
    "lname": fields.String,
    "email": fields.String,
    "pro_pic": fields.String,
    "bio": fields.String
}

post_output_fields = {
    "pid": fields.Integer,
    "title": fields.String,
    "description": fields.String,
    "timestamp": fields.DateTime,
    "uid": fields.Integer
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument("uname")
create_user_parser.add_argument("fname")
create_user_parser.add_argument("lname")
create_user_parser.add_argument("email")
create_user_parser.add_argument("pwd")

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument("fname")
update_user_parser.add_argument("lname")
update_user_parser.add_argument("pro_pic")
update_user_parser.add_argument("bio")
update_user_parser.add_argument("pwd")

create_post_parser = reqparse.RequestParser()
create_post_parser.add_argument("title")
create_post_parser.add_argument("description")
create_post_parser.add_argument("timestamp")
create_post_parser.add_argument("uid")

update_post_parser = reqparse.RequestParser()
update_post_parser.add_argument("title")
update_post_parser.add_argument("description")


class UserAPI(Resource):
    @marshal_with(user_output_fields)
    def get(self, username=None):
        if username is None:
            raise NotFoundError(status_code=404)
        user = db.session.query(User).filter(User.uname == username).first()
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)

    def post(self):
        args = create_user_parser.parse_args()
        uname = args.get("uname", None)
        fname = args.get("fname", None)
        lname = args.get("lname", None)
        email = args.get("email", None)
        pwd = args.get("pwd", None)


        user = db.session.query(User).filter(User.email == email).first()

        if user:
            raise BusinessValidationError(
                status_code=400, error_code="BE101", error_message="Duplicate user found!")

        user = db.session.query(User).filter(User.uname == uname).first()

        if user:
            raise BusinessValidationError(
                status_code=400, error_code="BE102", error_message="Username not available!")

        user = User(uname, fname, lname, email, pwd)
        db.session.add(user)
        db.session.commit()

        return "", 200

    def delete(self, username=None):
        if username is None:
            try:
                comments = db.session.query(Comment).delete()
                followings = db.session.query(Following).delete()
                followers = db.session.query(Follower).delete()
                likes = db.session.query(Like).delete()
                images = db.session.query(Image).delete()
                posts = db.session.query(Post).delete()
                users = db.session.query(User).delete()
                db.session.commit()
            except:
                db.session.rollback()
            response = {
                "comments": comments,
                "followings": followings,
                "followers": followers,
                "likes": likes,
                "images": images,
                "posts": posts,
                "users": users
            }
            return json.dumps(response), 200

        user = db.session.query(User).filter(User.uname == username).first()

        if user:
            comments = db.session.query(Comment).filter(
                Comment.uid == user.uid).delete()
            followings = db.session.query(Following).filter(
                Following.uid == user.uid).delete()
            followers = db.session.query(Follower).filter(
                Follower.uid == user.uid).delete()
            likes = db.session.query(Like).filter(
                Like.uid == user.uid).delete()
            posts = db.session.query(Post).filter(
                Post.uid == user.uid).all()
            img_cnt = 0
            for post in posts:
                images = db.session.query(Image).filter(
                    Image.pid == post.pid).delete()
                img_cnt += images
            posts = db.session.query(Post).filter(
                Post.uid == user.uid).delete()
            db.session.delete(user)
            db.session.commit()
        else:
            raise NotFoundError(status_code=404)

        response = {
            "comments": comments,
            "followings": followings,
            "followers": followers,
            "images": img_cnt,
            "likes": likes,
            "posts": posts
        }

        return json.dumps(response), 200

    def put(self, username=None):
        if username is None:
            raise NotFoundError(status_code=404)
        args = update_user_parser.parse_args()
        fname = args.get("fname", None)
        lname = args.get("lname", None)
        pro_pic = args.get("pro_pic", None)
        bio = args.get("bio", None)
        pwd = args.get("pwd", None)

        user = db.session.query(User).filter(User.uname == username).first()

        if user is None:
            raise NotFoundError(status_code=404)

        if len(pwd) < 8:
            raise BusinessValidationError(
                status_code=400, error_code="BE103", error_message="Password must contain at least 8 characters!")

        user.fname = fname
        user.lname = lname
        user.pro_pic = pro_pic
        user.bio = bio
        user.pwd = pwd

        db.session.add(user)
        db.session.commit()

        return "", 200


class PostAPI(Resource):
    @marshal_with(post_output_fields)
    def get(self, postId=None):
        if postId is None:
            raise NotFoundError(status_code=404)
        post = db.session.query(Post).filter(Post.pid == postId).first()
        if post:
            return post
        else:
            raise NotFoundError(status_code=404)

    def post(self):
        args = create_post_parser.parse_args()
        title = args.get("title", None)
        description = args.get("description", None)
        timestamp = datetime.now()
        uid = args.get("uid", None)

        user = db.session.query(User).filter(User.uid == uid).first()
        if user is None:
            raise BusinessValidationError(
                status_code=400, error_code="BE104", error_message="User does not exist!")

        post = Post(title, description, timestamp, uid)
        db.session.add(post)
        db.session.commit()

        return post.pid, 200

    def delete(self, postId=None):
        if postId is None:
            try:
                images = db.session.query(Image).delete()
                comments = db.session.query(Comment).delete()
                likes = db.session.query(Like).delete()
                posts = db.session.query(Post).delete()
                db.session.commit()
            except:
                db.session.rollback()
            response = {
                "images": images,
                "comments": comments,
                "likes": likes,
                "posts": posts
            }
            return json.dumps(response), 200

        post = db.session.query(Post).filter(Post.pid == postId).first()

        if post:
            images = db.session.query(Image).filter(
                Image.pid == post.pid).delete()
            comments = db.session.query(Comment).filter(
                Comment.pid == post.pid).delete()
            likes = db.session.query(Like).filter(
                Like.pid == post.pid).delete()
            posts = db.session.query(Post).filter(
                Post.pid == post.pid).delete()
            db.session.delete(post)
            db.session.commit()
        else:
            raise NotFoundError(status_code=404)

        response = {
            "images": images,
            "comments": comments,
            "likes": likes,
            "posts": posts
        }

        return json.dumps(response), 200

    def put(self, postId=None):
        if postId is None:
            raise NotFoundError(status_code=404)
        args = update_post_parser.parse_args()
        title = args.get("title", None)
        description = args.get("description", None)

        post = db.session.query(Post).filter(Post.pid == postId).first()

        if post is None:
            raise NotFoundError(status_code=404)

        post.title = title
        post.description = description

        db.session.add(post)
        db.session.commit()

        return "", 200
