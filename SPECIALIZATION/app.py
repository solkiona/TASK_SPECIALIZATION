import os
from flask import session, Flask , render_template, url_for, request, redirect, send_from_directory

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

from sqlalchemy.sql import func

from werkzeug.utils import secure_filename

upload_folder = 'static/uploads'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)
    
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = '9b3fa6c4ce0885cbdba98f128d27121e8cbd363865a3cd589fefb00dd61c829e'

db = SQLAlchemy(app)




class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookTitle = db.Column(db.String(100), nullable=False)
    bookAuthor = db.Column(db.String(100), nullable=False)
    yearPublished = db.Column(db.String(80), nullable=False)
    coverImage = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(1000), nullable=False)
    filepath = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f'<Book {self.bookTitle}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    
    def __repr_(self):
        return f'<User {self.username}>'
    
@app.route('/')
def index():
    students = Book.query.all()
    return render_template('index.html', students=students)


@app.route('/home/')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('navbar.html', user_id=user_id)
    return render_template('navbar.html')


@app.route('/about/')
def about():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('about.html', user_id=user_id)
    return render_template('about.html')

@app.route('/fileupload/' , methods=['GET', 'POST'])
def fileupload():
    if request.method == 'POST':
    
        if 'file1' not in request.files or 'file2' not in request.files:
            alert_message = '* Required file'
            return render_template('create.html', alert_message=alert_message)
        
        fileX = request.files['file1']
        fileY = request.files['file2']

        if fileX.filename == '' or fileY.filename == '':
            alert_message = '* Required file'
            return render_template('create.html', alert_message=alert_message)
        
        filenameX = secure_filename(fileX.filename)
        filenameY = secure_filename(fileY.filename)
        
        fileX.save(os.path.join(upload_folder, filenameX))
        fileY.save(os.path.join(upload_folder, filenameY))
        
        bookTitle = request.form['bookTitle']   
        bookAuthor = request.form['bookAuthor'] 
        yearPublished = request.form['yearPublished']
        description = request.form['description'] 
        coverImage = os.path.relpath(os.path.join(upload_folder, filenameX).replace('\\', '/'), upload_folder)
        filepath = os.path.relpath(os.path.join(upload_folder, filenameY).replace('\\', '/'), upload_folder)
        
        new_book = Book(bookTitle=bookTitle, bookAuthor=bookAuthor, yearPublished=yearPublished, coverImage=coverImage, Description=description, filepath=filepath)
        book_status = new_book
        db.session.add(new_book)
        db.session.commit()
        
        return redirect(url_for('books'))
    
    return render_template('create.html')
        
        
        
@app.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if 'signinBtn' in request.form and request.form['signinBtn'] == 'Signin':        
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter(and_(User.password == password, User.email == email)).first()
            if user:
                session['user_id'] = user.id
                if user.admin == True:
                    admin_status = True
                    return redirect(url_for('dashboard', admin_status= admin_status))
                else:
                    alert_message = 'User is not Admin'
                return redirect(url_for('login', alert_message=alert_message))
            
            else:
                alert_message = 'Invalid Credentials'
                return redirect(url_for('login', alert_message=alert_message))
        
        if 'signupBtn' in request.form and request.form['signupBtn'] == 'Signup':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # user = User.query.filter(and_(User.password == password, User.email == email)).first()
            user = User.query.filter(User.email == email).first()
            
            if not user:
                newUser = User(username=username, email=email, password=password, admin=True)   
                db.session.add(newUser)
                db.session.commit()
                
                session['user_id'] = newUser.id
                newUser.id = newUser.id
                return redirect(url_for('dashboard'))
            
            elif user:
                alert_message = "User Already Exist | Kindly Sign In"
                return redirect(url_for('admin_login', alert_message=alert_message))
    
    alert_message = request.args.get('alert_message', None)
    return render_template('login.html', alert_message=alert_message)



@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'signinBtn' in request.form and request.form['signinBtn'] == 'Signin':        
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter(and_(User.password == password, User.email == email)).first()
            if user:
                session['user_id'] = user.id
                if user.admin == True:
                    admin_status = True
                    return redirect(url_for('dashboard', admin_status=admin_status))
                else: 
                    return redirect(url_for('dashboard'))
            else:
                alert_message = 'Invalid Credentials'
                return redirect(url_for('login', alert_message=alert_message))
        
        if 'signupBtn' in request.form and request.form['signupBtn'] == 'Signup':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # user = User.query.filter(and_(User.password == password, User.email == email)).first()
            user = User.query.filter(User.email == email).first()
            
            if not user:
                newUser = User(username=username, email=email)
                newUser = User(username=username, email=email, password=password)
                    
                db.session.add(newUser)
                db.session.commit()
                session['user_id'] = newUser.id
                newUser.id = newUser.id
                return redirect(url_for('dashboard'))
            else:
                alert_message = "User Already Exist | Kindly Sign In"
                return redirect(url_for('login', alert_message=alert_message))
    
    alert_message = request.args.get('alert_message', None)
    return render_template('login.html', alert_message=alert_message)

@app.route('/books/')
def books():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        book_status = Book.query.all()
        return render_template('books.html', user_id=user_id , book_status=book_status)
    return render_template('books.html')

@app.route('/download/<filename>')
def download_file(filename):
    directory = 'static/uploads/'
    return send_from_directory(directory, filename)

@app.route('/dashboard/')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        admin_status = request.args.get('admin_status')
        return render_template('dashboard.html', admin_status=admin_status,user=user)
    else:
        return redirect(url_for('login'))
    
@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('home'))



@app.route('/addbooks/', methods=('GET', 'POST'))
def addbooks():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        admin_status = request.args.get('admin_status')
        return render_template('create.html', admin_status=admin_status,user=user)  
        

        
@app.post('/<int:book_id>/delete/')
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    return render_template('books.html')

if __name__ == '__main__':
    app.run(debug=True)
