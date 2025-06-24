from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Resume, Suggestion, Job

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    resume = Resume.query.filter_by(user_id=current_user.id).first()
    return render_template('dashboard.html', resume=resume)

@app.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    if request.method == 'POST':
        resume = Resume(
            name=request.form['name'],
            email=request.form['email'],
            skills=request.form['skills'],
            experience=request.form['experience'],
            education=request.form['education'],
            user_id=current_user.id
        )
        db.session.add(resume)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('resume.html')

@app.route('/suggestion', methods=['GET', 'POST'])
def suggestion():
    if request.method == 'POST':
        interest = request.form['interest']
        suggestion = Suggestion.query.filter_by(interest=interest).first()
        return render_template('suggestion.html', interest=interest, suggestion=suggestion)
    return render_template('suggestion.html', interest=None, suggestion=None)

@app.route('/jobs')
def jobs():
    jobs = Job.query.all()
    return render_template('jobs.html', jobs=jobs)

@app.route('/admin/jobs', methods=['GET', 'POST'])
def admin_jobs():
    if request.method == 'POST':
        job = Job(
            title=request.form['title'],
            company=request.form['company'],
            location=request.form['location'],
            description=request.form['description'],
            link=request.form['link']
        )
        db.session.add(job)
        db.session.commit()
        return redirect(url_for('admin_jobs'))
    jobs = Job.query.all()
    return render_template('admin_jobs.html', jobs=jobs)

@app.route('/admin/suggestions', methods=['GET', 'POST'])
def admin_suggestions():
    suggestions = Suggestion.query.all()
    if request.method == 'POST':
        interest = request.form['interest']
        text = request.form['text']
        new_suggestion = Suggestion(interest=interest, suggestion=text)
        db.session.add(new_suggestion)
        db.session.commit()
        return redirect(url_for('admin_suggestions'))
    return render_template('admin_suggestions.html', suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)
