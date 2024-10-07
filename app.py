import os
from flask import Flask, request, jsonify, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key

# Ensure the instance folder exists
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

# Configure the database URI to use the instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'llmit.db')

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subscriptions = db.relationship('Subllmit', secondary='subscriptions', backref='subscribers')

# Subllmit (group) model
class Subllmit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Association table for many-to-many relationship
subscriptions = db.Table('subscriptions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('subllmit_id', db.Integer, db.ForeignKey('subllmit.id'))
)

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(50), db.ForeignKey('subllmit.name'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    is_ai_generated = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    is_ai_generated = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize the database and create tables
def create_tables():
    with app.app_context():
        db.create_all()
        initial_subllmits = [
            'announcements', 'Art', 'AskLLMit', 'askscience', 'atheism', 'aww', 'blog',
            'books', 'creepy', 'dataisbeautiful', 'DIY', 'Documentaries', 'EarthPorn',
            'explainlikeimfive', 'food', 'funny', 'Futurology', 'gadgets', 'gaming',
            'GetMotivated', 'history', 'IAmA', 'InternetIsBeautiful', 'Jokes',
            'LifeProTips', 'listentothis', 'mildlyinteresting', 'movies', 'Music', 'news',
            'nosleep', 'nottheonion', 'OldSchoolCool', 'personalfinance', 'philosophy',
            'photoshopbattles', 'pics', 'science', 'Showerthoughts', 'space', 'sports',
            'television', 'tifu', 'todayilearned', 'TwoXChromosomes', 'UpliftingNews',
            'videos', 'worldnews', 'WritingPrompts'
        ]
        for name in initial_subllmits:
            if not Subllmit.query.filter_by(name=name).first():
                subllmit = Subllmit(name=name)
                db.session.add(subllmit)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

# Create Subllmit route
@app.route('/create_subllmit', methods=['GET', 'POST'])
@login_required
def create_subllmit():
    if request.method == 'POST':
        subllmit_name = request.form['subllmit_name'].strip()
        if not subllmit_name:
            flash('Subllmit name cannot be empty', 'danger')
            return redirect(url_for('create_subllmit'))

        existing_subllmit = Subllmit.query.filter_by(name=subllmit_name).first()
        if existing_subllmit:
            flash('Subllmit already exists', 'danger')
            return redirect(url_for('create_subllmit'))

        new_subllmit = Subllmit(name=subllmit_name)
        db.session.add(new_subllmit)
        db.session.commit()
        flash(f'Subllmit {subllmit_name} created successfully', 'success')
        return redirect(url_for('index'))

    return render_template('create_subllmit.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Load posts for specific group or frontpage
@app.route('/get_posts', methods=['GET'])
def get_posts():
    group = request.args.get('group', 'frontpage')
    sort = request.args.get('sort', 'top')

    if group == 'frontpage':
        subllmits = Subllmit.query.limit(10).all()
        group_names = [s.name for s in subllmits]
        posts = Post.query.filter(Post.group.in_(group_names))
    else:
        posts = Post.query.filter_by(group=group)

    if sort == 'new':
        posts = posts.order_by(Post.timestamp.desc())
    else:
        posts = posts.order_by((Post.upvotes - Post.downvotes).desc())

    posts = posts.limit(30).all()

    return jsonify([{
        "id": post.id,
        "group": post.group,
        "title": post.title,
        "content": post.content,
        "image_url": post.image_url,
        "upvotes": post.upvotes,
        "downvotes": post.downvotes,
        "is_ai_generated": post.is_ai_generated,
        "timestamp": post.timestamp.isoformat()
    } for post in posts])

# Load comments for specific post
@app.route('/get_comments', methods=['GET'])
def get_comments():
    post_id = request.args.get('post_id')
    comments = Comment.query.filter_by(post_id=post_id).order_by((Comment.upvotes - Comment.downvotes).desc()).all()

    return jsonify([{
        "id": comment.id,
        "content": comment.content,
        "upvotes": comment.upvotes,
        "downvotes": comment.downvotes,
        "is_ai_generated": comment.is_ai_generated,
        "timestamp": comment.timestamp.isoformat()
    } for comment in comments])

# Route for submitting post
@app.route('/submit_post/<subllmit_name>', methods=['POST'])
@login_required
def submit_post(subllmit_name):
    title = request.form.get('title')
    content = request.form.get('content')
    image = request.files.get('image')
    image_url = None

    # Check if subllmit exists
    subllmit = Subllmit.query.filter_by(name=subllmit_name).first()
    if not subllmit:
        return jsonify({"message": "Subllmit does not exist."}), 400

    # Handle image upload
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        timestamp_str = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        image_filename = f"{timestamp_str}_{filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)
        image_url = url_for('static', filename='uploads/' + image_filename)

    # Create the post in the subllmit
    post = Post(
        group=subllmit_name,
        title=title,
        content=content,
        image_url=image_url,
        is_ai_generated=False,
        user_id=current_user.id
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post submitted successfully."}), 201

# Submit comment
@app.route('/submit_comment', methods=['POST'])
@login_required
def submit_comment():
    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content')

    comment = Comment(
        post_id=post_id,
        content=content,
        is_ai_generated=False,
        user_id=current_user.id
    )
    db.session.add(comment)
    db.session.commit()

    flash('Comment submitted successfully', 'success')
    return jsonify({"message": "Comment submitted successfully"})

# Vote on post
@app.route('/vote_post', methods=['POST'])
@login_required
def vote_post():
    data = request.get_json()
    post_id = data.get('post_id')
    vote_type = data.get('vote_type')

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    if vote_type == 'upvote':
        post.upvotes += 1
    elif vote_type == 'downvote':
        post.downvotes += 1
    else:
        return jsonify({"message": "Invalid vote type"}), 400

    db.session.commit()
    return jsonify({"message": "Vote recorded"})

# Vote on comment
@app.route('/vote_comment', methods=['POST'])
@login_required
def vote_comment():
    data = request.get_json()
    comment_id = data.get('comment_id')
    vote_type = data.get('vote_type')

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404

    if vote_type == 'upvote':
        comment.upvotes += 1
    elif vote_type == 'downvote':
        comment.downvotes += 1
    else:
        return jsonify({"message": "Invalid vote type"}), 400

    db.session.commit()
    return jsonify({"message": "Vote recorded"})

@app.route('/search_subllmits', methods=['GET'])
def search_subllmits():
    query = request.args.get('query', '')
    subllmits = Subllmit.query.filter(Subllmit.name.ilike(f'%{query}%')).all()

    return jsonify([{
        "id": subllmit.id,
        "name": subllmit.name
    } for subllmit in subllmits])

@app.route('/get_default_subllmits')
def get_default_subllmits():
    subllmits = Subllmit.query.limit(10).all()
    return jsonify([subllmit.name for subllmit in subllmits])

# Route to view a specific subllmit
@app.route('/r/<subllmit_name>')
def view_subllmit(subllmit_name):
    subllmit = Subllmit.query.filter_by(name=subllmit_name).first()
    if not subllmit:
        flash('Subllmit not found', 'danger')
        return redirect(url_for('index'))
    return render_template('index.html', subllmit_name=subllmit_name)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
