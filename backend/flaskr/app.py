from datetime import date
from werkzeug.utils import secure_filename
from flaskr import app,db,mail
from flask import render_template,request,abort,redirect,url_for,flash,request,jsonify
from .models import Blog,Home,Knowledge,Post,Paragraph,User,PendUser,Comment,Like,Newsletter
from werkzeug.utils import secure_filename
from sqlalchemy import desc 
import os
from flask_login import current_user,login_user,logout_user,login_required
from .forms import LoginForm,RegistrationForm,RequestResetForm,ResetPasswordForm, UpdateAccountForm
from flask_mail import Message
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from PIL import Image
import secrets




bcrypt=Bcrypt(app)
app.config['SECRET_KEY']='d8827d6ff69e5fc8d4792ba5'
admin=Admin(app)
class Controller(ModelView):
    def is_accessible(self):
        if current_user:
            return current_user.is_authenticated
        # else:
        #     abort(422)
      

    def not_auth(self):
        return " you are not authorized to use the admin dashboard "

admin.add_view(Controller(User,db.session))
admin.add_view(Controller(Blog,db.session))
admin.add_view(Controller(Home,db.session))
admin.add_view(Controller(Knowledge,db.session))
admin.add_view(Controller(Paragraph,db.session))
admin.add_view(Controller(Post,db.session))
admin.add_view(Controller(PendUser,db.session))
admin.add_view(Controller(Comment,db.session))
admin.add_view(Controller(Like,db.session))

# authentication


@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) 
    form=LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email=form.email.data
            user=User.query.filter_by(email=email).first()

            if user:
                if bcrypt.check_password_hash(user.password,form.password.data):
                    login_user(user,form.remeber.data)
                    next_page=request.args.get('next')
                    
                    flash('User login successful','success')
                    return redirect(next_page) if next_page else redirect(url_for('home'))
                else:             
                    flash("Login Unsuccessful.Please check email and password",'danger')
                    return redirect(url_for('login'))
   
    return render_template('blog/login.html',form=form)
# registration
@app.route('/register',methods=['GET','POST'])
def register(): 
    if current_user.is_authenticated:
        return redirect(url_for('login')) 
    form=RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():     
            hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            username=form.username.data
            email=form.email.data
            if email and hashed_password:
                user=PendUser(username=username,password=hashed_password,email=email)
                

                db.session.add(user)
                db.session.commit()  
                comfirm_email(user)
                flash(f'A mail has been sent to the email address you entered .Confirm your email by clicking the link that was sent to your email .Thank your','success')
                return redirect(url_for('login'))
    if request.method == 'GET':
        
         return render_template('blog/sign-up-2.html',form=form)
    return render_template('blog/sign-up-2.html',form=form)

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():   
    logout_user()
    flash('logged out ','successful')
    return redirect(url_for('home'))

# start email confirmation during registration
def comfirm_email(user):
    token=user.get_verify_email_token()
    msg = Message('Confirm Username',
    sender='noreply@demo.com',
    recipients=[user.email])
    msg.body=f'''confirm your email:
    {url_for('email_token',token=token,_external=True)}
    we want to confirm if this mail is yours 
    '''
    mail.send(msg)


@app.route('/email/<token>',methods=['GET','POST'])
def email_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=PendUser.verify_email_token(token)
    if user is None:
        flash('this is an invalid token or expired token ')
        return redirect(url_for('register'))

    if user:
        email=user.email
        password=user.password
        username=user.username
        confirm_password=User(username=username,password=password,email=email)
        db.session.add(confirm_password)
        db.session.commit()
        flash('Email Confirmed')
        return redirect(url_for('home'))
# end of email confirmation during registration

# start of forgot password verification
def send_reset_email(user):
    token=user.get_reset_token()
    msg = Message('Password Rest Request',
    sender='noreply@nautilus.com',
    recipients=[user.email])
    msg.body=f'''to reset your password ,visit the following link:
    {url_for('reset_token',token=token,_external=True)}
    if  you did not make this request then simply ignore this email and no changes will be made
    '''
    mail.send(msg)

   
@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        email=form.email.data
        user=User.query.filter_by(email=email).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password','success')
        return redirect(url_for('login'))
    return render_template('blog/reset_request.html',title="reset password",form=form)
@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash('this is an invalid token or expired token','danger')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():     
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()  
        flash('Your password changed')
        return redirect(url_for('login'))
        
    return render_template('blog/reset_token.html',title='Reset password',form=form)

# end of forgot password verification




@app.route('/blog')
def blog():
    page=request.args.get('page',1,type=int)
    query=Blog.query.order_by(desc(Blog.date)).paginate(page=page,per_page=12)
    know=Knowledge.query.order_by(desc(Knowledge.date)).all()
    post=Post.query.order_by(desc(Post.date)).paginate(page=page,per_page=4)

    return render_template('blog/blog-list.html',query=query,know=know,post=post)
@app.route('/blog/<int:blog_id>')
def blog_details(blog_id):
    months_in_year = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    

    query=Blog.query.filter_by(id=blog_id).first()
    if query is None :
        abort(404)
    
    return render_template('blog/blog1.html',query=query,months=months_in_year[(query.date.month)-1])
@app.route('/blogpost',methods=['GET','POST'])
def blogpost():
    image=request.files.get('image',None)
    UPLOAD_FOLDER='backend/flaskr/static/akdablog'
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    if request.method == 'POST':
        if image is not None:
            topic=request.form.get('topic',None)
            content=request.form.get('message',None)
            facebook_link=request.form.get('facebook_link',None)
            instagram_link=request.form.get('instagram_link',None)
            twitter_link=request.form.get('twitter_link',None)
            github_link=request.form.get('github_link',None)
            image_file=secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],image_file))

            blog=Blog(topic=topic,details=content,facebook=facebook_link,instagram=instagram_link,twitter=twitter_link,github=github_link,image_file=image_file)
            db.session.add(blog)
            db.session.commit()
            return redirect(url_for('blog'))
        if image is None:
            abort(411)

    return render_template('blog/blogpost.html')
@app.route('/knowledge',methods=['GET','POST'])
def knowpost():
    image=request.files.get('image',None)
    UPLOAD_FOLDER='backend/flaskr/static/knowledge'
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    if request.method == 'POST':
        if image is not None:
            topic=request.form.get('topic',None)
            know=secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],know))
            knowledge=Knowledge(topic=topic,image_file=know)
            db.session.add(knowledge)
            db.session.commit()
            return redirect(url_for('blog'))

        if image is None:
            abort(411)
    return render_template('blog/knowpost.html')

    


@app.route('/portfolio')
def portfolio():
    return render_template('blog/portfolio1.html')
@app.route('/project')
def project():
    return render_template('blog/project.html')
@app.route('/post',methods=['GET','POST'])
def post():
    page=request.args.get('page',1,type=int)
    query=Post.query.paginate(page=page,per_page=4)
    blog=Blog.query.order_by(desc(Blog.date)).paginate(page=page,per_page=4)

   

    return render_template('blog/post.html',query=query,blog=blog)




@app.route('/post/<int:post_id>',methods=['GET','POST'])
def posts_detail(post_id):
    query=Post.query.filter_by(id=post_id).first()
    image=request.files.get('image',None)
    UPLOAD_FOLDER='backend/flaskr/static/images'
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    if request.method == 'POST':
        if image is not None:
            know=secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],know))
            description=request.form.get('description')
            post=Paragraph(image_file=know,description=description,post_id=query.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('post'))
        if image is None:
            description=request.form.get('description')
            post=Paragraph(description=description,post_id=query.id)
            db.session.add(post)
            db.session.commit()

    paragraph=Paragraph.query.filter_by(post_id=query.id).all()

    return render_template('blog/post_details.html',query=query,paragraph=paragraph)


    




@app.route('/create_post',methods=['GET','POST'])
def create_post():
    image=request.files.get('image',None)
    UPLOAD_FOLDER='backend/flaskr/static/knowledge'
    app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
    if request.method == 'POST':
        if image is not None:
            know=secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],know))
            topic=request.form.get('topic',None)
            posts=request.form.get('post',None)
            post=Post(topic=topic,posts=posts,image_file=know)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('post'))

    return render_template('blog/post_create.html')


@app.route('/')
def home():
    query1=Home.query.filter_by(id=1).first()
    query2=Home.query.filter_by(id=2).first()
    query3=Home.query.filter_by(id=5).first()
    query4=Home.query.filter_by(id=4).first()
    query5=Home.query.filter_by(id=5).first()
    query={
        'query1':query1,
        'query2':query2,
        'query3':query3,
        'query4':query4,
        'query5':query5
    }
   
    
    return render_template('blog/home.html',query=query)

@app.route('/test')
def test():
    return render_template('blog/home-chat.html')


@app.route('/create-comment/<blog_id>',methods=['GET','POST'])
def create_comment(blog_id):
    text=request.form.get('text',None)
    if  text is None:
        flash('comment cannot be empty')
    else:
        query=Blog.query.filter_by(id=blog_id).first()
        if query:
            comment=Comment(text=text,author=current_user.id,blog_id=query.id)
            db.session.add(comment)
            db.session.commit()
    return redirect(request.url)



@app.route('/like-blog/<blog_id>',methods=['GET'])
def like_blog(blog_id):
    query=Blog.query.filter_by(id=blog_id).first()
    like=Like.query.filter_by(author=current_user.id,blog_id=query.id).first()
    if query is  None:
        return jsonify({'error':'post does not exist.'},411)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like=Like(author=current_user.id,blog_id=blog_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes":len(query.likes),'liked':current_user.id in map(lambda x: x.author,query.likes)})


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex + f_ext
    picture_path=os.path.join(app.root_path,'static/profile',picture_fn)
    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/profile/<string:username>',methods=['GET','POST'])
def profiLe(username):
    query=User.query.filter_by(username=username).first()
    if query is None:
        flash('Username does not exits in our data',category='danger')
    elif query.username !=current_user.username:
        flash("Access denied ,you can't make changes to this profile")
    form=UpdateAccountForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.picture.data:              
                picture_file=save_picture(form.picture.data)
                current_user.image_file=picture_file
            current_user.about=form.about.data
            current_user.username=form.username.data
            current_user.facebook=form.facebook.data
            current_user.instagram=form.instagram.data
            current_user.twitter=form.twitter.data
            current_user.github=form.github.data
            current_user.website=form.website.data
            current_user.number=form.number.data
            
            db.session.commit()
            flash('your account has been updated!','success')
            return redirect(url_for('profile'))
    if request.method == 'GET':
        form.username.data=current_user.username
        form.about.data=current_user.about
        form.facebook.data=current_user.facebook
        form.instagram.data=current_user.instagram
        form.twitter.data=current_user.twitter
        form.github.data=current_user.github
        form.website.data=current_user.website
        form.number.data=current_user.number

    user=int(current_user.id)
    
    # profile=User.query.filter_by(user_id=user).first()
    user_profile=User.query.filter_by(id=user).first()

    return render_template('blog/account.html',title='Account'
    ,image_file=current_user.image_file
    ,form=form
    ,user=user_profile,)




  

   
@app.route('/newsletter',methods=['GET','POST'])
def newsletter():
    form=RequestResetForm()
    if form.validate_on_submit():
        email=form.email.data
        user=Newsletter.query.filter_by(email=email).first()
        send_reset_email(user)
        flash('An email has been sent to confirm your email address','success')
        return redirect(url_for('login'))
    return render_template('blog/reset_request.html',title="reset password",form=form)


def send_reset_email(user):
    token=user.get_reset_token()
    msg = Message('Confirm your email',
    sender='noreply@nautilus.com',
    recipients=[user.email])
    msg.body=f'''to reset your password ,visit the following link:
    {url_for('newsletter',token=token,_external=True)}
    if  you did not make this request then simply ignore this email and no changes will be made
    '''
    mail.send(msg)

@app.route('/newsletter/<token>',methods=['GET','POST'])
def newsletter_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash('this is an invalid token or expired token','danger')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():     
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()  
        flash('Your password changed')
        return redirect(url_for('login'))
        
    return render_template('blog/reset_token.html',title='Reset password',form=form)

@app.route('/watch')
def watch():
    return render_template('blog/watch.html')