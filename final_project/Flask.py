#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip3 install flask-session')


# In[ ]:


################################################################################################################

# EXTERNAL MODULES TO BE USED

################################################################################################################
import os
import secrets
from PIL import Image
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_session.__init__ import Session
from flask_bcrypt import Bcrypt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
bcrypt = Bcrypt(app)

################################################################################################################

# APP CONFIGURATION

################################################################################################################

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/workshop'
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_info.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'thisismysecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)

UPLOAD_FOLDER = 'static/profile_pics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

################################################################################################################

# SELF-DEFINED LOGIN MANAGER DECORATOR

################################################################################################################

def login_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash('You need to login first.','danger')
            return redirect(url_for('login'))
    return wrap

################################################################################################################

# DATA MODELS

################################################################################################################
db = SQLAlchemy(app)

# 帖子的话那个tag（就是在发帖的时候要选择在哪个板块发帖）我不知道怎么弄，这里是剩下的部分
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255))
    post_date = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    views = db.Column(db.Integer,default=0)
    comments = db.Column(db.Integer,default=0)
    types = db.Column(db.Text, nullable=False)
    racename1 = db.Column(db.Text, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(255))
    password = db.Column(db.String(80))
    bio = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean)
    image_file = db.Column(db.String(255), nullable=False, default='default.jpg')
#     active = db.Column(db.Boolean)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    message = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    post = db.relationship('Post', backref=db.backref('posts',lazy=True, passive_deletes=True))
    date_pub = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)   
    
class Race(db.Model):
    __tablename__ = 'races'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    character = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255))
#     image_file = db.Column(db.String(255))
    post_date = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    starttime = db.Column(db.Text, nullable=False)
    finishtime = db.Column(db.Text, nullable=False)
    qianyan = db.Column(db.Text, nullable=False)
    zhengtiguize = db.Column(db.Text, nullable=False)
    jutixize = db.Column(db.Text, nullable=False)
    saidao1 = db.Column(db.Text, nullable=False)
    saidao2 = db.Column(db.Text)
    saidao3 = db.Column(db.Text)
    saidao4 = db.Column(db.Text)
    saidao5 = db.Column(db.Text)
    saidao6 = db.Column(db.Text)
    saidaoshuoming = db.Column(db.Text, nullable=False)
    jianglishuoming = db.Column(db.Text, nullable=False)
    jiangjinzonge= db.Column(db.String(255))
    views = db.Column(db.Integer,default=0)

class Zhongchou(db.Model):
    __tablename__ = 'zhongchoulist'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    character = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    groupinfo = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer,default=0)

    
################################################################################################################

# WEB ROUTES FOR CONTROLLING ACCESS TO TEMPLATE VIEWS

################################################################################################################
    
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/pastrace-list")
def pastracelist():
    return render_template('pastrace-list.html')

@app.route("/pastrace-details")
def pastracedetails():
    return render_template('pastrace-details.html')


@app.route("/currentrace-list")
def currentracelist():
    return render_template('currentrace-list.html')

@app.route("/racetopic-list")
def racetopiclist():
    return render_template('racetopic-list.html')

@app.route("/help-problems")
def helpproblems():
    return render_template('help-problems.html')

@app.route("/help-contact")
def helpcontact():
    return render_template('help-contact.html')


@app.route("/currentrace-details")
def currentracedetails():
    return render_template('currentrace-details.html')

@app.route("/postrecord")
def postrecord():
    return render_template('postrecord.html')

@app.route("/race-rank")
def racerank():
    return render_template('race-rank.html')

# 比赛列表 12.2半夜进度
# @app.route('/currentrace-list')
# #@login_required
# def races():
#     page_num = 1
#     race_list = Race.query.paginate(per_page=6, page=page_num, error_out=True) 
#     return render_template('currentrace-list.html', races=race_list)

# @app.route("/currentrace-list/<int:page_num>")
# def races_paging(page_num):
#     race_list = Race.query.paginate(per_page=6, page=page_num, error_out=True) 
#     return render_template('currentrace-list.html', races=race_list)

# 比赛发布
@app.route("/postrace", methods=["GET","POST"])
@login_required
def postrace():
    msg = None
    if 'username' in session:
        msg = 'You are logged in as ' + session['username'] + '.'

    if request.method == "POST":
        title = request.form['title']
        character = request.form['character']
        starttime =request.form['starttime']
        finishtime =request.form['finishtime']
        qianyan = request.form['qianyan']
        zhengtiguize = request.form['zhengtiguize']
        jutixize = request.form['jutixize']
        saidao1 = request.form['saidao1']
        saidao2 = request.form['saidao2']
        saidao3 = request.form['saidao3']
        saidao4 = request.form['saidao4']
        saidao5 = request.form['saidao5']
        saidao6 = request.form['saidao6']
        saidaoshuoming = request.form['saidaoshuoming']
        jianglishuoming = request.form['jianglishuoming']
        jiangjinzonge = request.form['jiangjinzonge']
        author = session['username']
        
#         file = request.files['file']
#         print(file)

#         if file:
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#         image_file =os.path.join('/static/profile_pics', file.filename)
        
        postrace = Race(title=title,starttime=starttime,author=author,finishtime=finishtime,qianyan=qianyan,zhengtiguize=zhengtiguize,jutixize=jutixize,saidao1=saidao1,saidao2=saidao2,saidao3=saidao3,saidao4=saidao4,saidao5=saidao5,saidao6=saidao6,saidaoshuoming=saidaoshuoming,jianglishuoming=jianglishuoming,character=character)
        db.session.add(postrace)
        db.session.commit()
        msg = "发布成功"
        print("发布成功")
        
    return render_template('postrace.html', msg = msg)


# 发帖
@app.route("/postpost", methods=["GET","POST"])
@login_required
def postpost():
    msg = None
    if 'username' in session:
        msg = 'You are logged in as ' + session['username'] + '.'

    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        author = session['username']
        types = request.form['types']
        racename1 = request.form['racename1']
        postpost = Post(title=title,body=body,author=author,types=types,racename1=racename1)
        db.session.add(postpost)
        db.session.commit()
        msg = "发布成功"
        print("发布成功")
        
    return render_template('postpost.html', msg = msg)

# 帖子列表
@app.route('/topic-post-list')
#@login_required
def posts():
    page_num = 1
    post_list = Post.query.paginate(per_page=6, page=page_num, error_out=True)
    return render_template('topic-post-list.html', posts=post_list)

@app.route("/topic-post-list/<int:page_num>")
def posts_paging(page_num):
    post_list = Post.query.paginate(per_page=6, page=page_num, error_out=True) 
    return render_template('topic-post-list.html', posts=post_list)

# 帖子详情
@app.route("/post_details/<int:id>",methods=['GET',"POST"])
def post_details(id):
    dataset = []
    post = Post.query.filter_by(id=id).first()
    print("post.views=",post.views,"post.title=",post.title,"post.author", post.author,"post.racename1=",post.racename1)
    dataset.append({"title":post.title, "body":post.body, "author":post.author, "post_date":post.post_date, "comments":post.comments,"views":post.views,"racename1":post.racename1 })
    comment = Comment.query.filter_by(post_id=post.id).all()
    post.views = post.views + 1
    comment_count = post.comments
    db.session.commit()
    Thanks =""
    if request.method =="POST":
        post_id = post.id
        name = request.form.get('name')
        message = request.form.get('message')
        comment = Comment(name=name,message=message,post_id=post_id)
        db.session.add(comment)
        post.comments = post.comments + 1
        db.session.commit()
        flash('Your comment has been submited.', 'success')
        return redirect(request.url)


    return render_template('post-details.html', posts=dataset, comment=comment, comment_count=comment_count, Thanks=Thanks, title=post.title)




# 发布众筹
@app.route("/post-zhongchou/", methods=["GET","POST"])
@login_required
def postzhongchou():
    msg = None
    if 'username' in session:
        msg = 'You are logged in as ' + session['username'] + '.'

    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        groupinfo = request.form['groupinfo']
        character = request.form['character']
        author = session['username']
        postzhongchou = Zhongchou(title=title,body=body,character=character,author=author,groupinfo=groupinfo)
        db.session.add(postzhongchou)
        db.session.commit()
        msg = "发布成功"
        print("发布成功")
        return render_template('zhongchou-list.html', msg = msg)

    return render_template('post-zhongchou.html', msg = msg)

# 众筹列表
@app.route('/zhongchou-list')
#@login_required
def zhongchoulist():
    page_num = 1
    zhongchou_list = Zhongchou.query.paginate(per_page=6, page=page_num, error_out=True) 
    return render_template('zhongchou-list.html', zhongchoulist=zhongchou_list)

@app.route("/zhongchou-list/<int:page_num>")
def zhongchou_paging(page_num):
    zhongchou_list = Zhongchou.query.paginate(per_page=6, page=page_num, error_out=True) 
    return render_template('zhongchou-list.html', zhongchoulist=zhongchou_list)


# 众筹详情
@app.route("/zhongchou-details/<int:id>",methods=['GET',"POST"])
def zhongchou_details(id):
    dataset = []
   
    zhongchou = Zhongchou.query.filter_by(id=id).first()
    print(id)
#     print("zhongchou.views=",zhongchou1.views,"zhongchou.title=",zhongchou1.title,"zhongchou.author=",zhongchou1.author,"zhongchou.character=",zhongchou1.character)
    dataset.append({"title":zhongchou.title, "body":zhongchou.body, "author":zhongchou.author, "post_date":zhongchou.post_date,"views":zhongchou.views,"character":zhongchou.character})
#     zhongchou1.views = zhongchou1.views + 1
    db.session.commit()
    Thanks =""

    return render_template('zhongchou-details.html', zhongchoulist=dataset,Thanks=Thanks,title=zhongchou.title)



# 个人主页
@app.route("/personal-profile/", defaults={"username": "nobody"})
@app.route("/personal-profile/<string:username>", methods=['GET', 'POST'])
@login_required
def personalprofile(username):
# def personalprofile(email):
    dataset = []
#     used for show data in frontend
    if request.method == "GET":
        msg = "Edit"
        user = User.query.filter_by(username=username).first()
#         user = User.query.filter_by(email=email).first()
        if user.image_file is None:
            user.image_file = 'default.jpg'
            image_file = url_for('static', filename='profile_pics/' + user.image_file)
        dataset.append({'id':user.id, 'username': user.username,'email': user.email,'bio': user.bio, 'image_file':user.image_file})
#    update data in sqlite     
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        bio = request.form['bio']
        id = request.form['id']
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        print("Updated")
        msg = "Updated!"
        user = User.query.filter_by(id=id).first()
        user.username = username
        user.email = email
        user.bio = bio
        user.image_file =os.path.join('/static/profile_pics', file.filename)
        db.session.commit()
        dataset.append({'id':user.id, 'username': user.username,'email': user.email,'bio': user.bio,'image_file':user.image_file})

    return render_template('personal-profile.html', entries=dataset)

# 登录
@app.route("/login", methods=["GET","POST"])
def login():
    msg = None
    if 'username' in session:
        msg = 'You are logged in as ' + session['username'] + '.'
#          msg = 'You are logged in as ' + session['email'] + '.'

    if request.method == "POST":
        username = request.form['username']
#         email = request.form['email']
        password = request.form['password']
#         print(email, password)
        user = User.query.filter_by(username=username).first()
#         user = User.query.filter_by(email=email).first()
        if not user:
            print("Account does not exist!")
            msg = "Account does not exist!"
        else:
            if bcrypt.check_password_hash(user.password, password):
                session['logged_in'] = True
                session['username'] = user.username
#                 session['email'] = user.email
                session['admin'] = user.admin
                print("Welcome!")
                msg = "Welcome!"
                return redirect(url_for('personalprofile', username=username))
#                 return redirect(url_for('profile', username=username))
#                     email ersion
#                 return redirect(url_for('personalprofile', email=email))
            msg = "Wrong password!"

    return render_template('login.html', msg = msg)

# 登出
@app.route("/logout")
@login_required
def logout():
    session.clear()
#     return render_template('index.html')
    return render_template('index.html')


# 注册
@app.route("/register", methods=["GET","POST"])
def register():
    
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        bio = request.form['bio']
        password = request.form['password']
#         print(username,email,bio,password)
        password = bcrypt.generate_password_hash(password)
        admin = 0
        user = User(username=username,email=email,bio=bio,password=password,admin=admin)
        db.session.add(user)
        db.session.commit()
        print("You have been registered!")

    return render_template('register.html')

################################################################################################################

# ERROR HANDLERS

################################################################################################################

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

################################################################################################################

# APPLICATION TEST RUN AT PORT 9004

################################################################################################################

if __name__ == '__main__':
    app.run('localhost', 9004)


# In[ ]:





# In[ ]:




