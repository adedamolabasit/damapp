from sqlalchemy.orm import backref
from flaskr import app,db,login_manager
from datetime import datetime, timezone
from itsdangerous import Serializer, TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    __tablename__='user'
    


    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(21),unique=True)
    email=db.Column(db.String(112))
    image_file=db.Column(db.String(211),nullable=True,default='118d39bdbbd2e366.png')
    password=db.Column(db.String(211))
    is_admin=db.Column(db.Boolean(),default=False)
    is_staff=db.Column(db.Boolean(),default=False)
    about=db.Column(db.String(552),nullable=True)
    facebook=db.Column(db.String(65),nullable=True)
    instagram=db.Column(db.String(65),nullable=True)
    twitter=db.Column(db.String(65),nullable=True)
    github=db.Column(db.String(65),nullable=True)
    website=db.Column(db.String(65),nullable=True) 
    number=db.Column(db.Integer,nullable=True)
    posts=db.relationship('Post',backref='user',cascade='all,delete',lazy=True)
    comments=db.relationship('Comment',backref='user',cascade='all,delete',lazy=True)
    blogs=db.relationship('Blog',backref='user',cascade='all,delete',lazy=True)
    likes=db.relationship('Like',backref='user',cascade='all,delete',lazy=True)
    
    def __repr__(self):
        return f'<username {self.username},id {self.id}>'
    def get_reset_token(self,expires_sec=1200):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')  
    @staticmethod
    def verify_reset_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:  
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class PendUser(db.Model):
    __tablename__='penduser'


    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(21))
    email=db.Column(db.String(112))
    password=db.Column(db.String(211))
    def get_verify_email_token(self,expires_sec=1200):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    @staticmethod
    def verify_email_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:  
            user_id = s.loads(token)['user_id']
        except:
            return None
        return PendUser.query.get(user_id)




class Home(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    headings=db.Column(db.String(),nullable=True)
    details=db.Column(db.Text,nullable=True)


class Blog(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    topic=db.Column(db.String(55),nullable=True)
    details=db.Column(db.Text,nullable=True)
    image_file=db.Column(db.String(211),nullable=True)
    date=db.Column(db.DateTime,nullable=True,default=datetime.now)
    facebook=db.Column(db.Text,nullable=True)
    instagram=db.Column(db.Text,nullable=True)
    twitter=db.Column(db.Text,nullable=True)
    github=db.Column(db.Text,nullable=True)
    comments=db.relationship('Comment',backref='blog',cascade='all,delete',lazy=True)
    likes=db.relationship('Like',backref='blog_likes',cascade='all,delete',lazy=True)
    author=db.Column(db.Integer,db.ForeignKey('user.id'),nullable='True')


class Knowledge(db.Model):
    id= db.Column(db.Integer,primary_key='True')
    topic=db.Column(db.Text,nullable=True)
    image_file=db.Column(db.Text,nullable=True)
    date=db.Column(db.DateTime,default=datetime.now())


class Post(db.Model):
    __tablename__='post'
    id=db.Column(db.Integer,primary_key=True)
    topic=db.Column(db.String(),nullable=True)
    posts=db.Column(db.Text,nullable=True)
    image_file=db.Column(db.Text,nullable=True)
    date=db.Column(db.DateTime,default=datetime.now())
    author=db.Column(db.Integer,db.ForeignKey('user.id'),nullable='True')
    paragraph=db.relationship('Paragraph',backref='post', cascade='all,delete',lazy=True)
    comments=db.relationship('Comment',backref='post',cascade='all,delete',lazy=True)
    likes=db.relationship('Like',backref='post_likes',cascade='all,delete',lazy=True)

class Paragraph(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    image_file=db.Column(db.Text,nullable=True)
    description=db.Column(db.Text,nullable=True)
    post_id=db.Column(db.Integer,db.ForeignKey('post.id'),nullable=False)

class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    text=db.Column(db.Text,nullable=True)
    date=db.Column(db.DateTime(timezone=True),default=datetime.now())
    author=db.Column(db.Integer,db.ForeignKey('user.id'),nullable='True')
    post_id=db.Column(db.Integer,db.ForeignKey('post.id',),nullable='True')
    blog_id=db.Column(db.Integer,db.ForeignKey('blog.id',),nullable='True')

class Like(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.DateTime(timezone=True),default=datetime.now())
    author=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=True)
    blog_id=db.Column(db.Integer,db.ForeignKey('blog.id'),nullable=True)
    post_id=db.Column(db.Integer,db.ForeignKey('post.id'),nullable=True)


class Newsletter(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.Text,nullable=True)
    date=db.Column(db.DateTime(timezone=True),default=datetime.now())
    def get_reset_token(self,expires_sec=1200):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')  
    @staticmethod
    def verify_reset_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:  
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)



