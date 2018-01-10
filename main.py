from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'xydkSSzkj334slkjx69al'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
                
@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()

    return render_template('index.html', title='Blog Users', users=users)


@app.route('/blog')
def blog():

    
    blog_id = request.args.get('id')
    blogger_id = request.args.get('user')

    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('singleBlog.html', blog=blog)

    if blogger_id:
        blogs = Blog.query.filter_by(owner_id=blogger_id).all()
        return render_template('singleUser.html', blogs=blogs)

    blogs = Blog.query.all()

    return render_template('blogs.html', title='Blogz!', blogs=blogs)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():


    if request.method == 'POST':
        title_error = ''
        body_error = ''
        blog_title = request.form['title']
        blog_body = request.form['body']
        

        if len(blog_title) < 1:
            title_error = 'Please fill in the title.'

        if len(blog_body) < 1:
            body_error = 'Please fill in the body.'

        if not title_error and not body_error:
            blog_owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title, blog_body, blog_owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}.html'.format(new_blog.id))
        else:

            return render_template('addblog.html', title='Add Blog Entry',
            title_error=title_error, body_error=body_error)

    return render_template('addblog.html', title='Add Blog Entry')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''
        verify_password_error = ''

        if not username or not password or not verify:
            username_error = 'abc'
            flash('One or more fields were left blank.', 'error')
        else:
            username = username
            if len(username) < 3 or len(password) < 3:
                username_error = 'abc'
                flash('Usernames and passwords must be at least 3 characters long.', 'error')

        if password == verify:
            verify = verify
        else:
            verify_password_error = 'abc'
            flash('Passwords do not match.', 'error')

        if existing_user:
            flash('Duplicate user', 'error')

        if not username_error and not password_error and not verify_password_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')

        return render_template('signup.html')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():

    if 'username' in session:
        flash('You are already logged in.', 'error')
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User does not exist, please register.', 'error')
        elif user.password == password:
            session['username'] = username
            flash('Logged in', 'error')
            return redirect('/newpost')
        else:
            flash('User password is incorrect', 'error')

    return render_template('login.html')      

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blogs')



if __name__ == '__main__':
    app.run()
