from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ok'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Alexandru.Ojica/PycharmProjects/flaskProject/notes.db'
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        notes = Note.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', notes=notes)
    return render_template('index.html')


@app.route('/debug_db')
def debug_db():
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        output = []

        for table in tables:
            output.append(f"Table: {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                output.append(f"  Column: {column['name']} - Type: {column['type']}")

        return "<br>".join(output)
    except Exception as e:
        return str(e)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_note = Note(title=title, content=content, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_note.html')


@app.route('/edit_note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    if note.user_id != current_user.id:
        return redirect(url_for('index'))
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_note.html', note=note)


@app.route('/delete_note/<int:id>')
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    if note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for('index'))


def print_tables():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(len(tables))

    for table in tables:
        print(f"Table: {table}")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  Column: {column['name']} - Type: {column['type']}")


if __name__ == '__main__':
    app.run(debug=True)
