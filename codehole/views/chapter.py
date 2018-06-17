# pylint: disable=all

from flask import Blueprint, request, abort, jsonify
from flask import redirect, render_template, url_for
blueprint = Blueprint('chapter', __name__, url_prefix='/chapter')

from codehole.db import db, BookModel, ChapterModel
from codehole.core import random_id


@blueprint.route(
    '/book/<book_id>/chapter/<chapter_id>',
    methods=["GET"], endpoint="chapter")
def chapter_page(self, book_id, chapter_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for("home"))
    chapter = ChapterModel.query.get(chapter_id)
    if not chapter or chapter.book_id != book_id:
        return redirect(url_for("book", book_id=book_id))
    return render_template("chapter.html", book=book, chapter=chapter)


@blueprint.route(
    '/book/<book_id>/chapter/add.json', endpoint="add_chapter_api")
def add_chapter(self, book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for("home"))
    title = request.form.get('title', '').trim()
    if not title:
        abort(400)
    chapter_id = random_id()
    chapter = ChapterModel(
        id=chapter_id,
        book_id=book_id,
        ordinal=book.next_ordinal,
        title=title)
    db.session.add(chapter)
    book.next_ordinal += 1
    book.chapters_count += 1
    db.session.commit()
    return jsonify({'ok': True})


@blueprint.route(
    '/book/<book_id>/chapter/<chapter_id>/save.json',
    methods=['POST'], endpoint="save_chapter_api")
def edit_chapter(self, book_id, chapter_id):
    book = BookModel.query.get(book_id)
    if not book:
        abort(404)
    chapter = ChapterModel.query.get(chapter_id)
    if not chapter:
        abort(404)
    if chapter.book_id != book_id:
        abort(400)
    source = request.form.get('source', '').trim()
    last_version = int(request.form.get('version', '').trim() or 0)
    if chapter.version != last_version:
        abort(412)
    chapter.source = source
    chapter.version += 1
    db.session.commit()
    return jsonify({'ok': True})
