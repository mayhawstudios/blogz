from flask import Flask, request, redirect, render_template,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1234567'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self,title,body,user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref='user')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/")
def index():
    index = User.query.all()
    return render_template('index.html',index=index)

@app.route("/blog")
def blog():
    owner_id = request.args.get('user')

    if owner_id:
        entries = Blog.query.filter_by(owner_id=owner_id).order_by(Blog.id.desc()).all()
    else:
        entries = Blog.query.order_by(Blog.id.desc()).all()

    return render_template('blog.html',entries=entries)

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        u_error = ""
        p_error = ""

        if user and user.password == password:
            session['username'] = username
            return redirect("/newpost")
        else:
            if username == "":
                u_error = "Field cannot be blank"
            
            if password == "":
                p_error = "Field cannot be blank"

            if not user:
                u_error = "Username incorrect or does not exist."
                return render_template('login.html',username=username,u_error=u_error,p_error=p_error)
                         
            if user.password != password:
                p_error = "Incorrect password."
            
            return render_template('login.html',username=username,u_error=u_error,p_error=p_error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/signup",methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify']
        user = User.query.filter_by(username=username).first()
        u_error = ""
        p_error = ""
        v_error = ""
        is_error = False

        if user:
            is_error = True
            u_error = "Username already exists."
        
        if len(username) < 3:
            is_error = True
            u_error = "Username must be more than three characters."

        if len(password) < 3:
            is_error = True
            p_error = "Password must be more than three characters."
        
        if password != verify_password:
            is_error = True
            v_error = "Does not match password."
        
        if username == "":
            is_error = True
            u_error = "Username cannot be blank."
        
        if password == "":
            is_error = True
            p_error = "Password cannot be blank."
        
        if verify_password == "":
            is_error = True
            v_error = "Verify Password cannot be blank."
        
        if is_error:
            return render_template('signup.html',username=username,u_error=u_error,v_error=v_error,p_error=p_error)
        else:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")

    return render_template('signup.html')

@app.route("/newpost", methods=['POST','GET'])
def newpost():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        t_error = ""
        b_error = ""

        if title == "":
            t_error = "Please add a title to your post."
        
        if body == "":
            b_error = "Please write a post for your blog here."
        
        if t_error != "" or b_error != "":
            return render_template('newpost.html', title=title, body=body, 
            t_error=t_error, b_error=b_error)
        else:
            user_id = User.query.filter_by(username=session['username']).first()
            new_entry = Blog(title,body,user_id)
            db.session.add(new_entry)
            db.session.commit()
            newentry = Blog.query.order_by(Blog.id.desc()).first()
            id = newentry.id

            return redirect("/blogpost?id="+str(id))

    return render_template('newpost.html')

@app.route("/blogpost", methods=['GET'])
def blogpost():
    id = request.args.get('id')
    entry = Blog.query.filter_by(id=id).first()

    return render_template('blogpost.html', entry=entry)

if __name__ == '__main__':
    app.run()