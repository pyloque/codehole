# pylint: disable=all

from flask import render_template, Blueprint
from codehole.db import BookModel, ArticleModel

blueprint = Blueprint("home", __name__, url_prefix='/')


@blueprint.route("/")
def home():
    books = BookModel.query.all()
    articles = (
        ArticleModel.query
        .order_by(ArticleModel.create_date.desc())
        .limit(10).all())
    return render_template(
        "home.html", articles=articles, books=books)
