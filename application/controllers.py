from datetime import datetime
from flask import request, flash
from flask import render_template, redirect, url_for
from flask import current_app as app
from flask_login import login_user, login_required, current_user, logout_user
from application.models import *
from application.validation import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os


@app.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("index.html", current_user=current_user)


@app.route("/home", methods=["GET"])
@login_required
def home():
    posts = []
    for following in current_user.followings:
        user = db.session.query(User).filter(User.uid == following.fid).first()
        posts += user.posts
    posts.sort(reverse=True, key=lambda x: x.timestamp)
    return render_template("home.html", current_user=current_user, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    message = None
    if request.method == "POST":
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        try:
            user = User.query.filter_by(uname=uname).first()
            if not check_password_hash(user.pwd, pwd):
                raise Exception("Invalid credentials!")
            login_user(user, remember=False)
        except:
            message = "Invalid credentials!"
            return render_template("login.html", message=message)
        return redirect(url_for("home"))
    return render_template("login.html", message=message)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    message = None
    if request.method == "POST":
        uname = request.form["uname"]
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        pwd = generate_password_hash(request.form["pwd"])

        try:
            user = db.session.query(User).filter(User.email == email).first()

            if user:
                raise Exception("Duplicate user found!")

            user = db.session.query(User).filter(User.uname == uname).first()

            if user:
                raise Exception("Username not available!")

            user = User(uname, fname, lname, email, pwd)
            db.session.add(user)
            db.session.commit()

            flash("Account created successfully! Please Login!", "login")
            return redirect(url_for("login"))

        except Exception as e:
            message = str(e)

    return render_template("signup.html", message=message)


@app.route('/<string:username>', methods=['GET'])
def profile(username):
    user = db.session.query(User).filter(User.uname == username).first()
    if user is None:
        raise NotFoundError(status_code=404)

    _following = None
    if current_user.is_authenticated:
        for following in current_user.followings:
            if following.fid == user.uid:
                _following = True
                break
        else:
            _following = False
    else:
        _following = False
    return render_template("profile.html", current_user=current_user, user=user, following=_following)


@app.route('/top-posts', methods=['GET'])
def top_posts():
    posts = db.session.query(Post).all()
    posts.sort(reverse=True, key=lambda x: len(x.likes))
    return render_template("top_posts.html", current_user=current_user, posts=posts[0:min(len(posts), 12)])


@app.route("/post/<int:postId>", methods=["GET"])
def post(postId):
    post = db.session.query(Post).filter(Post.pid == postId).first()

    if post is None:
        raise NotFoundError(status_code=404)

    liked = None
    if current_user.is_authenticated:
        for like in current_user.likes:
            if like.pid == post.pid:
                liked = True
                break
        else:
            liked = False
    else:
        liked = False

    return render_template("post.html", current_user=current_user, post=post, liked=liked)


@app.route("/post/<int:postId>/add-comment", methods=["POST"])
@login_required
def add_comment(postId):

    post = db.session.query(Post).filter(Post.pid == postId).first()
    if post is None:
        raise NotFoundError(status_code=404)

    content = request.form["content"]

    if len(content) > 0:
        comment = Comment(content, datetime.now(), current_user.uid, postId)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for("post", postId=postId) + "#comments")


@app.route("/post/<int:postId>/update-like", methods=["GET"])
@login_required
def update_like(postId):
    post = db.session.query(Post).filter(Post.pid == postId).first()

    if post is None:
        raise NotFoundError(status_code=404)

    for like in current_user.likes:
        if like.pid == post.pid:
            db.session.delete(like)
            break
    else:
        new_like = Like(current_user.uid, post.pid)
        db.session.add(new_like)

    db.session.commit()
    return redirect(url_for("post", postId=postId) + "#likes")


@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        timestamp = datetime.now()
        uid = current_user.uid

        post = Post(title, description, timestamp, uid)
        db.session.add(post)
        db.session.commit()

        pid = post.pid

        if 'post-img' in request.files:
            file = request.files['post-img']

            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                post_img = filename

                if post_img:
                    img = Image(post_img, pid)
                    db.session.add(img)
                    db.session.commit()

        return redirect(url_for("post", postId=pid))
    return render_template("create_post.html", current_user=current_user)


@app.route("/edit-post/<int:postId>", methods=["GET", "POST"])
@login_required
def edit_post(postId):
    post = db.session.query(Post).filter(Post.pid == postId).first()

    if post is None or post not in current_user.posts:
        raise NotFoundError(status_code=404)

    if request.method == "POST":
        img = request.files["post-img"]
        filename = secure_filename(img.filename)
        if filename == "":
            filename = post.images[0].url if post.images else None
        else:
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        title = request.form["title"]
        description = request.form["description"]

        post = db.session.query(Post).filter(Post.pid == postId).first()

        if post is None:
            raise NotFoundError(status_code=404)

        post.title = title
        post.description = description

        db.session.add(post)
        db.session.commit()

        if filename:
            image = db.session.query(Image).filter(
                Image.pid == post.pid).first()

            if image:
                image.url = filename
            else:
                image = Image(filename, post.pid)

            db.session.add(image)
            db.session.commit()

        user = User.query.get(int(current_user.uid))
        login_user(user)
        return redirect(url_for("post", postId=post.pid))
    return render_template("edit_post.html", current_user=current_user, post=post)


@app.route("/delete-post/<int:postId>", methods=["GET"])
@login_required
def delete_post(postId):
    post = db.session.query(Post).filter(Post.pid == postId).first()

    if post is None or post not in current_user.posts:
        raise NotFoundError(status_code=404)

    db.session.query(Image).filter(
        Image.pid == post.pid).delete()
    db.session.query(Comment).filter(
        Comment.pid == post.pid).delete()
    db.session.query(Like).filter(
        Like.pid == post.pid).delete()
    db.session.query(Post).filter(
        Post.pid == post.pid).delete()
    db.session.delete(post)
    db.session.commit()

    user = User.query.get(int(current_user.uid))
    login_user(user)
    return redirect(url_for("profile", username=current_user.uname))


@app.route("/connection/<string:username>", methods=["GET"])
@login_required
def connection(username):
    user = db.session.query(User).filter(User.uname == username).first()

    if user is None:
        raise NotFoundError(status_code=404)

    for following in current_user.followings:
        if following.fid == user.uid:
            db.session.delete(following)
            for follower in user.followers:
                if follower.fid == current_user.uid:
                    db.session.delete(follower)
                    break
            break
    else:
        new_following = Following(current_user.uid, user.uid)
        new_follower = Follower(user.uid, current_user.uid)
        db.session.add(new_following)
        db.session.add(new_follower)
    db.session.commit()

    return redirect(url_for("profile", username=username))


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        print(request.files)
        img = request.files["pro-img"]
        filename = secure_filename(img.filename)
        if filename == "":
            filename = current_user.pro_pic
        else:
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        fname = request.form["fname"]
        lname = request.form["lname"]
        bio = request.form["bio"]
        pro_pic = filename
        pwd = generate_password_hash(request.form["pwd"])

        user = db.session.query(User).filter(
            User.uname == current_user.uname).first()

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

        user = User.query.get(int(current_user.uid))
        login_user(user)
        return redirect(url_for("profile", username=current_user.uname))
    return render_template("edit_profile.html", current_user=current_user)


@app.route("/search/users", methods=["GET", "POST"])
def search_users():
    users = db.session.query(User).all()
    query = ""
    if request.method == "POST":
        query = request.form["query"]
        users = db.session.query(User).filter((User.uname.like(
            query + "%")) | (User.fname.like(query + "%")) | (User.lname.like(query + "%"))).all()
        return render_template("search_users.html", current_user=current_user, users=users, query=query)
    return render_template("search_users.html", current_user=current_user, users=users, query=query)


@app.route("/search/posts", methods=["GET", "POST"])
def search_posts():
    posts = db.session.query(Post).all()
    query = ""
    if request.method == "POST":
        query = request.form["query"]
        posts = db.session.query(Post).filter((Post.title.like(
            "%" + query + "%")) | (Post.description.like("%" + query + "%"))).all()
        return render_template("search_posts.html", current_user=current_user, posts=posts, query=query)
    return render_template("search_posts.html", current_user=current_user, posts=posts, query=query)


@app.route("/following/<string:username>", methods=["POST", "GET"])
def following(username):
    query = ""
    user = db.session.query(User).filter(User.uname == username).first()
    if user is None:
        raise NotFoundError(status_code=404)
    if request.method == "POST":
        query = request.form["query"]
        users = []
        for f in user.followings:
            fuser = db.session.query(User).filter(User.uid == f.fid).first()
            if fuser.uname.startswith(query) or fuser.fname.startswith(query) or fuser.lname.startswith(query):
                users.append(fuser)
    else:
        users = []
        for f in user.followings:
            fuser = db.session.query(User).filter(User.uid == f.fid).first()
            users.append(fuser)
    return render_template("following.html", current_user=current_user, user=user, users=users, query=query)


@app.route("/followers/<string:username>", methods=["POST", "GET"])
def followers(username):
    query = ""
    user = db.session.query(User).filter(User.uname == username).first()
    if user is None:
        raise NotFoundError(status_code=404)
    if request.method == "POST":
        query = request.form["query"]
        users = []
        for f in user.followers:
            fuser = db.session.query(User).filter(User.uid == f.fid).first()
            if fuser.uname.startswith(query) or fuser.fname.startswith(query) or fuser.lname.startswith(query):
                users.append(fuser)
    else:
        users = []
        for f in user.followers:
            fuser = db.session.query(User).filter(User.uid == f.fid).first()
            users.append(fuser)
    return render_template("followers.html", current_user=current_user, user=user, users=users, query=query)
