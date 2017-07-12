from flask import Flask, request, redirect, render_template,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:admin@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1234567'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self,title,body):
        self.title = title
        self.body = body

@app.route("/")
def index():
    entries = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html',entries=entries)

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
            return render_template('newpost.html', t_error=t_error, b_error=b_error)
        else:
            new_entry = Blog(title,body)
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
    title = entry.title
    body = entry.body

    return render_template('blogpost.html',title=title,body=body)

if __name__ == '__main__':
    app.run()