# pylint: disable=all

from flask import request, Blueprint, abort
from flask import redirect, render_template, url_for
blueprint = Blueprint('book', __name__, url_prefix='/book')

from codehole.db import db, BookModel
from codehole.core import random_id


@blueprint.route(
    '/book/<book_id>', methods=["GET"], endpoint="book")
def book_home(self, book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for("home"))
    return render_template("book.html", book=book)


default_icon = ''
default_qrcode = ''


@blueprint.route(
    '/book/add.json', methods=["POST"], endpoint="add_book_api")
def book_add(self):
    author = request.form.get('author', '').trim()
    title = request.form.get('title', '').trim()
    book_id = random_id()
    book = BookModel(
        id=book_id, author=author, title=title,
        icon=default_icon, qrcode=default_qrcode)
    tips = []
    if not book.author:
        tips.append('作者不能为空')
    if not book.title:
        tips.append('标题不能为空')
    errors = ''.join(tips)
    if errors:
        abort(400)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('show_book_update', book=book, tips=[]))


@blueprint.route(
    '/book/update/<book_id>', methods=["GET"], endpoint="show_book_update")
def show_book_update(self, book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for('home'))
    tips = []
    return render_template("book_edit.html", book=book, tips=tips)


@blueprint.route(
    '/book/update/<book_id>', methods=["POST"], endpoint="book_update")
def book_update(self, book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for('home'))
    author = request.form.get('author', '').trim()
    title = request.form.get('title', '').trim()
    icon = request.form.get('icon', '').trim() or default_icon
    qrcode = request.form.get('qrcode', '').trim() or default_qrcode
    book.author = author
    book.title = title
    book.icon = icon
    book.qrcode = qrcode
    db.session.commit()
    return redirect(url_for('book', book_id=book_id))
