# pylint: disable=all


from flask import request, Blueprint, abort, jsonify
from flask import redirect, render_template, url_for
blueprint = Blueprint('book', __name__, url_prefix='/book')

from codehole.db import db, BookModel, ChapterModel
from codehole.core import random_id
from codehole.core import markdown


@blueprint.route(
    '/', methods=["GET"], endpoint="book_list")
def book_list():
    books = BookModel.query.all()
    if not books:
        return redirect(url_for("home.home"))
    return render_template("book_list.html", books=books)


@blueprint.route(
    '/<book_id>', methods=["GET"], endpoint="book")
def book_home(book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for("home"))
    chapters = (
        ChapterModel.query
        .filter(ChapterModel.book_id == book_id)
        .order_by(ChapterModel.ordinal.asc())
        .all())
    return render_template("book.html", book=book, chapters=chapters)


default_icon = 'https://user-gold-cdn.xitu.io/2018/6/2/163beaa5525c6b6b?imageView2/2/w/480/h/480/q/85/interlace/1'
default_qrcode = 'https://user-gold-cdn.xitu.io/2018/6/1/163bb4b6cd0ecaf2?w=258&h=258&f=jpeg&s=27486'


@blueprint.route(
    '/new', methods=["GET"], endpoint="book_new")
def book_new():
    return render_template("book_new.html")


@blueprint.route(
    '/new', methods=["POST"])
def book_create():
    author = request.form.get('author', '').strip()
    title = request.form.get('title', '').strip()
    book_id = random_id()
    book = BookModel(
        id=book_id, author=author, title=title,
        icon=default_icon, qrcode=default_qrcode)
    if not author or not title:
        abort(400)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('.book_edit', book_id=book_id))


@blueprint.route(
    '/edit/<book_id>', methods=["GET"], endpoint="book_edit")
def book_edit(book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for('home.home'))
    return render_template("book_edit.html", book=book)


@blueprint.route(
    '/edit/<book_id>', methods=["POST"])
def book_update(book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for('home.home'))
    author = (request.form.get('author') or '').strip()
    title = (request.form.get('title') or '').strip()
    icon = (request.form.get('icon') or '').strip()
    qrcode = (request.form.get('qrcode') or '').strip()
    source = (request.form.get('source') or '').strip()
    version = (request.form.get('version') or '').strip()
    if not author or not title or not icon or not qrcode or not version:
        abort(400)
    version = int(version)
    if version != book.version:
        abort(412)
    book.author = author
    book.title = title
    book.icon = icon
    book.qrcode = qrcode
    book.source = source
    book.version += 1
    book.html = markdown(source)
    db.session.commit()
    return redirect(url_for('book.book', book_id=book_id))


@blueprint.route(
    '/edit_chapters/<book_id>',
    methods=["GET"], endpoint="book_chapters_edit")
def book_edit_chapters(book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for('home.home'))
    chapters = (
        ChapterModel.query
        .filter(ChapterModel.book_id == book.id)
        .order_by(ChapterModel.ordinal.asc())
        .all())
    return render_template(
        "book_chapters_edit.html", book=book, chapters=chapters)


@blueprint.route(
    '/<book_id>/chapter/add.json', methods=["POST"], endpoint="add_chapter_api")
def add_chapter(book_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for("home.home"))
    title = (request.form.get('title') or '').strip()
    version = (request.form.get('version') or '').strip()
    if not title or not version:
        abort(400)
    version = int(version)
    if version != book.version:
        abort(412)
    chapter_id = random_id()
    chapter = ChapterModel(
        id=chapter_id,
        book_id=book_id,
        ordinal=book.next_ordinal,
        title=title)
    db.session.add(chapter)
    book.next_ordinal += 1
    book.chapters_count += 1
    book.version += 1
    db.session.commit()
    return jsonify({'ok': True})


@blueprint.route(
    '/<book_id>/chapter/<chapter_id>/edit_title.json',
    methods=["POST"], endpoint="edit_chapter_title_api")
def edit_chapter_title(book_id, chapter_id):
    book = BookModel.query.get(book_id)
    if not book:
        abort(404)
    chapter = ChapterModel.query.get(chapter_id)
    if not chapter:
        abort(404)
    title = (request.form.get('title') or '').strip()
    if not title:
        abort(400)
    chapter.title = title
    db.session.commit()
    return jsonify({'ok': True})


@blueprint.route(
    '/<book_id>/chapter/swap.json',
    methods=["POST"], endpoint="swap_chapters")
def swap_chapters(book_id):
    book = BookModel.query.get(book_id)
    if not book:
        abort(404)
    source_id = (request.form.get('source_id') or '').strip()
    target_id = (request.form.get('target_id') or '').strip()
    version = (request.form.get('version') or '').strip()
    version = int(version)
    if version != book.version:
        abort(412)
    if not source_id:
        abort(400)
    source = ChapterModel.query.get(source_id)
    target = None
    if target_id:
        target = ChapterModel.query.get(target_id)
        if not target:
            abort(400)
    if not target:
        source.ordinal = book.next_ordinal
        book.next_ordinal += 1
        book.version += 1
        db.session.commit()
    else:
        chapters = (
            ChapterModel.query
            .filter(ChapterModel.ordinal >= target.ordinal)
            .filter(ChapterModel.book_id == book_id)
            .order_by(ChapterModel.ordinal.desc())
            .all())
        for chapter in chapters:
            chapter.ordinal += 1
            db.session.flush()
        book.next_ordinal += 1
        book.version += 1
        db.session.flush()
        source.ordinal = chapter.ordinal - 1
        db.session.commit()
    return jsonify({'ok': True})


@blueprint.route(
    '/<book_id>/chapter/<chapter_id>',
    methods=["GET"], endpoint="chapter")
def chapter_page(book_id, chapter_id):
    book = BookModel.query.get(book_id)
    if not book:
        return redirect(url_for("home.home"))
    chapter = ChapterModel.query.get(chapter_id)
    if not chapter or chapter.book_id != book_id:
        return redirect(url_for("book", book_id=book_id))
    rows = (
        ChapterModel.query
        .with_entities(ChapterModel.id)
        .order_by(ChapterModel.ordinal)
        .all())
    chapter_ids = [row.id for row in rows]
    chapter_idx = chapter_ids.index(chapter.id)
    chapter.index = chapter_idx
    return render_template("chapter.html", book=book, chapter=chapter)


@blueprint.route(
    '/book/<book_id>/chapter/<chapter_id>/edit',
    methods=['GET'], endpoint="edit_chapter")
def edit_chapter(book_id, chapter_id):
    book = BookModel.query.get(book_id)
    if not book:
        abort(404)
    chapter = ChapterModel.query.get(chapter_id)
    if not chapter:
        abort(404)
    if chapter.book_id != book_id:
        abort(400)
    return render_template("chapter_edit.html", book=book, chapter=chapter)


@blueprint.route(
    '/book/<book_id>/chapter/<chapter_id>/edit',
    methods=['POST'])
def update_chapter(book_id, chapter_id):
    book = BookModel.query.get(book_id)
    if not book:
        abort(404)
    chapter = ChapterModel.query.get(chapter_id)
    if not chapter:
        abort(404)
    if chapter.book_id != book_id:
        abort(400)
    source = request.form.get('source', '').strip()
    version = int(request.form.get('version', '').strip())
    if chapter.version != version:
        abort(412)
    chapter.source = source
    chapter.html = markdown(source)
    chapter.version += 1
    db.session.commit()
    return redirect(
        url_for('book.chapter', book_id=book_id, chapter_id=chapter_id))
