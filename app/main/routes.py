from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .models import Note
from ..extensions import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    notes = Note.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=6)
    return render_template('index.html', notes=notes)


@main.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_note = Note(title=title, content=content, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('add_note.html')


@main.route('/edit_note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    if note.user_id != current_user.id:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        data = request.get_json()
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        db.session.commit()
        return jsonify({'success': True}), 200
    return render_template('edit_note.html', note=note)


@main.route('/delete_note/<int:id>')
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    if note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for('main.index'))
