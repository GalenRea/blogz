from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy 
import sys


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '12345abcde'


class Diary(db.Model):
    '''
    Stores blog entries
    '''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(4000))
    writer_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__ (self, title, body, writer_id):
        self.title = title
        self.body = body
        self.writer_id = writer_id
    
    def is_valid(self):
        '''
        all blanks must be filled in for a valid blog post
        '''
        if self.title and self.body:
            return True
        else:
            return False

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True,)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Diary', backref='writer')

    def __init__ (self, email, password):
        self.email = email
        self.password = password



    

@app.route('/')
def index():
    users = Users.query.all()
    return render_template('users.html', users=users)

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'home', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect ('/login')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']      
        user = Users.query.filter_by(email=email).first()
        print(user.password)
        if user and user.password == password:
            session['email'] = email
            flash("logged in")
            return redirect ('/new_entry')
        else:
            flash('user password is either inorrect or does not exist', 'error')
    return render_template('login.html')

def validate_login():
    #username_error=''
    password_error=''
    verify_error=''
    email_error=''
    #username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    #if username == "":
        #username_error='Enter a valid username'
    
    for letter in password:
        if letter.isalpha() == False:
            password_error = "Passwords must contain alphanumeric characters only"
    
    if email == "":
        email_error = "Please enter a valid email"

    for letter in email:
        if letter == ' ':
            email_error = "Email may not contain spaces"
            
    if email.count('@', 0, 40) != 1: 
        email_error = "Email may only contain '@' once"
    
    if email.count('.', 0, 40) != 1: 
        email_error = "Email may only contain one period"

    if len(email) < 3 or len(email) > 20:
        email_error = "Email must be between 3 and 20 characters"

    if password_error != '' and email_error != '':
        return render_template("new_entry_form.html", password_error = password_error, 
        email_error = email_error)

    else:
        return redirect("/blog")


@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        user = Users(email = email, password = password)
        db.session.add(user)
        db.session.commit()
        #session['email']=users.email
        return redirect ('/new_entry')





    return render_template('register.html')


    

def validate_reg():
    #username_error=''
    password_error=''
    verify_error=''
    email_error=''
    #username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    email = request.form['email']
    #if username == "":
        #username_error='Enter a valid username'

    if len(password) < 3 or len(password) > 20:
        password_error = "Password must be between 3 and 20 characters"
    
    if password != verify:
       verify_error = "Passwords must match"
    
    for letter in password:
        if letter.isalpha() == False:
            password_error = "Passwords must contain alphanumeric characters only"
    
    if email == "":
        email_error = "Please enter a valid email"

    for letter in email:
        if letter == ' ':
            email_error = "Email may not contain spaces"
            
    if email.count('@', 0, 40) != 1: 
        email_error = "Email may only contain '@' once"
    
    if email.count('.', 0, 40) != 1: 
        email_error = "Email may only contain one period"

    if len(email) < 3 or len(email) > 20:
        email_error = "Email must be between 3 and 20 characters"

    if password_error != '' or verify_error != '' or email_error != '':
        return render_template("index.html", password_error = password_error, 
        verify_error = verify_error, email_error = email_error)

    else:
        return redirect("/blog")

#@app.route("/")
#def index():
    #return redirect("/blog")

@app.route('/blog') 
def blog():
    entry_id = request.args.get('id')
    user_id = request.args.get('userid')
    if (user_id):
        user = Users.query.get(user_id)
        return render_template('single_user.html', user=user)
    
    if (entry_id): 
        entry = Diary.query.get(entry_id)
        writer_id = entry.writer_id
        user = Users.query.get(writer_id)
        return render_template('single_entry.html', title ="Blog Title", entry=entry, user=user)

        #blog_title = request.form['Blog']
        #new_blog = Blog(blog_title, blog_body)
        #db.session.add(new_blog)
        #db.session.commit()
    #return render_template('index.html', title=title, body=body) 

    sort = request.args.get('sort')
    if (sort=="newest"):
        all_entries = Diary.query.order_by(Diary.created.desc()).all()
    else:
        all_entries = Diary.query.all()
    return render_template('all_entries.html', title = "All Entries", all_entries=all_entries)

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    '''
    GET: Requests info from the server to display on the browser
    POST: gets info from the user on browser to save to the server
    '''
    
    if request.method == 'POST':
        new_entry_title = request.form['title']
        new_entry_body = request.form['body'] 
        email = session['email']
        user = Users.query.filter_by(email=email).first()
        new_entry = Diary(new_entry_title, new_entry_body, user.id)
    
        if new_entry.is_valid():
            db.session.add(new_entry)
            db.session.commit()
            url = "/blog?id=" + str(new_entry.id)
            return redirect(url)
        else:
            flash("Please fill in all required fields")
            return redirect('/new_entry')
            #title="Create new blog entry",
            #new_entry_title=new_entry_title
            #new_entry_body=new_entry_body

    else: #GET request
        return render_template('new_entry_form.html', title="Create new blog entry")

if __name__ == '__main__':
    app.run()



 