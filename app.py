from flask import Flask, render_template, redirect, session, flash
from forms import UserForm, LoginForm, FeedbackForm
from models import db, connect_db, User, Feedback
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "oh-so-secret"

connect_db(app)

with app.app_context():
    db.create_all()

@app.route("/")
def root():
    """Render homepage."""

    return render_template("index.html")

@app.route('/users/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    if username == session['username']:
        feedback = Feedback.query.filter_by(username=username).all()
        return render_template('user.html', user=user, feedbacks=feedback)
    flash("You don't have permission to do that!", "danger")
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def feedback(username):
    if 'username' not in session: 
        flash("Please login first!", "danger")
        return redirect('/')
    if username == session['username']:

        form = FeedbackForm()
        
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(title=title, content=content, user=user)
            db.session.add(new_feedback)
            db.session.commit()
            flash('New feedback successful!', 'success')
            return redirect(f'/users/{username}')
        
        return render_template('feedback.html', form=form, username=username)
    flash("You don't have permission to do that!", "danger")
    return redirect('/')

@app.route('/feedback/<int:feedback_id>/update', methods=['GET','POST'])
def edit_feedback(feedback_id):
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username == session['username']:
        form = FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            
            db.session.commit()
            flash("Feedback edited!", "info")
            return redirect(f'/users/{feedback.username}')
        
        return render_template('edit_feedback.html', form=form, feedback=feedback)
        
    flash("You don't have permission to do that!", "danger")
    return redirect('/')

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username == session['username']:
        user = User.query.filter_by(username=feedback.username).first()
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "info")
        return redirect(f'/users/{feedback.username}', user=user)
    flash("You don't have permission to do that!", "danger")
    return redirect('/')

@app.route("/register", methods=["GET", "POST"])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.error.append('Username already taken! Please pick another.')
            return render_template ('register.html', form=form) 
        
        session['username'] = new_user.username
        flash(f'Welcome {new_user.username}!', 'success')
        return redirect(f"/users/{new_user.username}")
    return render_template('register.html', form=form)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    if username != session['username']:
        flash("You don't have permission to do that!", "danger")
        return redirect('/')
    session.pop('username')
    db.session.delete(user)
    db.session.commit()
    flash('User deleted!', 'error')
    return redirect('/login')
    
@app.route("/login", methods=['GET', 'POST'])
def login_user():
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome, {user.first_name}', "primary")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid login credentials!']
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("You have been successfully signed out.")
    return redirect('/')