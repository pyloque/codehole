# pylint: disable=all
from flask import Blueprint, request, abort
from flask import redirect, render_template, url_for
blueprint = Blueprint('article', __name__, url_prefix='/article')

from codehole.db import db, ArticleModel
from codehole.core import random_id
from codehole.core import markdown


@blueprint.route("/", methods=["GET"], endpoint="article_list")
def article_list():
    articles = (
        ArticleModel.query
        .order_by(ArticleModel.create_date.desc())
        .limit(20).all())
    return render_template(
        "article_list.html", articles=articles)


@blueprint.route(
    '/<article_id>', methods=["GET"], endpoint="article")
def article_page(article_id):
    article = ArticleModel.query.get(article_id)
    if not article:
        return redirect(url_for("home"))
    return render_template("article.html", article=article)


@blueprint.route(
    '/new', methods=["GET"], endpoint="article_new")
def article_new():
    return render_template("article_new.html")


@blueprint.route(
    '/new', methods=["POST"])
def article_create():
    title = (request.form.get('title') or '').strip()
    author = (request.form.get('author') or '').strip()
    if not title or not author:
        abort(400)
    article_id = random_id()
    article = ArticleModel(
        id=article_id, title=title, author=author, icon='')
    db.session.add(article)
    db.session.commit()
    return redirect(url_for('.article_edit', article_id=article_id))


@blueprint.route(
    '/edit/<article_id>', methods=["GET"], endpoint="article_edit")
def article_edit(article_id):
    article = ArticleModel.query.get(article_id)
    if not article:
        return redirect(url_for("home"))
    return render_template("article_edit.html", article=article)


@blueprint.route(
    '/edit/<article_id>', methods=["POST"])
def article_update(article_id):
    article = ArticleModel.query.get(article_id)
    if not article:
        return redirect(url_for("home"))
    title = (request.form.get('title') or '').strip()
    author = (request.form.get('author') or '').strip()
    icon = (request.form.get('icon') or '').strip()
    summary = (request.form.get('summary') or '').strip()
    source = (request.form.get('source') or '').strip()
    version = (request.form.get('version') or '').strip()
    if not title or not author or not icon or not version:
        abort(400)
    version = int(version)
    if version != article.version:
        abort(400)
    html = markdown(source)
    article.title = title
    article.author = author
    article.icon = icon
    article.summary = summary
    article.source = source
    article.html = html
    article.is_draft = False
    article.version += 1
    db.session.commit()
    return redirect(url_for('.article', article_id=article_id))
