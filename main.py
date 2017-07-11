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
        body = request.form['title']

        new_entry = Blog(title,body)
        db.session.add(new_entry)
        db.session.commit()

        return redirect("/")

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()