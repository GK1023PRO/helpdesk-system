from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# -----------------------
# Configuration
# -----------------------
app.config['SECRET_KEY'] = 'helpdesk_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://admin:admin123@localhost:5432/helpdesk')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# -----------------------
# Models
# -----------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    tickets = db.relationship('Ticket', backref='owner', lazy=True)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(20), default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='ticket', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author = db.relationship('User', backref='comments')

# -----------------------
# Login Manager
# -----------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------
# Routes - Home
# -----------------------
@app.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    else:
        tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('index.html', tickets=tickets)

# -----------------------
# Routes - Register
# -----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# -----------------------
# Routes - Login
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

        login_user(user)
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

# -----------------------
# Routes - Logout
# -----------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# -----------------------
# Routes - Create Ticket
# -----------------------
@app.route('/ticket/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        priority = request.form['priority']

        if not title or not description:
            flash('Title and description are required.', 'danger')
            return render_template('create_ticket.html')

        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            user_id=current_user.id
        )
        db.session.add(ticket)
        db.session.commit()

        flash('Ticket created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_ticket.html')

# -----------------------
# Routes - View Ticket
# -----------------------
@app.route('/ticket/<int:id>')
@login_required
def view_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    if current_user.role != 'admin' and ticket.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    return render_template('view_ticket.html', ticket=ticket)

# -----------------------
# Routes - Edit Ticket
# -----------------------
@app.route('/ticket/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    if current_user.role != 'admin' and ticket.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        priority = request.form['priority']
        status = request.form['status']

        if not title or not description:
            flash('Title and description are required.', 'danger')
            return render_template('edit_ticket.html', ticket=ticket)

        ticket.title = title
        ticket.description = description
        ticket.priority = priority
        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Ticket updated successfully!', 'success')
        return redirect(url_for('view_ticket', id=ticket.id))

    return render_template('edit_ticket.html', ticket=ticket)

# -----------------------
# Routes - Delete Ticket
# -----------------------
@app.route('/ticket/<int:id>/delete')
@login_required
def delete_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    if current_user.role != 'admin' and ticket.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket deleted successfully!', 'success')
    return redirect(url_for('index'))

# -----------------------
# Routes - Add Comment
# -----------------------
@app.route('/ticket/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    ticket = Ticket.query.get_or_404(id)
    content = request.form['content'].strip()

    if not content:
        flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('view_ticket', id=id))

    comment = Comment(
        content=content,
        user_id=current_user.id,
        ticket_id=id
    )
    db.session.add(comment)
    db.session.commit()

    flash('Comment added successfully!', 'success')
    return redirect(url_for('view_ticket', id=id))

# -----------------------
# Routes - Dashboard (Admin)
# -----------------------
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('index'))

    total = Ticket.query.count()
    open_tickets = Ticket.query.filter_by(status='Open').count()
    in_progress = Ticket.query.filter_by(status='In Progress').count()
    closed = Ticket.query.filter_by(status='Closed').count()
    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()

    return render_template('dashboard.html',
                           total=total,
                           open_tickets=open_tickets,
                           in_progress=in_progress,
                           closed=closed,
                           recent_tickets=recent_tickets)

# -----------------------
# Run App
# -----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)