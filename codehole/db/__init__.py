# pylint: disable=all

from datetime import datetime
from collections import OrderedDict

from flask import current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(current_app)


class BookModel(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.String(256), primary_key=True)
    author = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(1024), nullable=False)
    icon = db.Column(db.String(1024), nullable=False)
    qrcode = db.Column(db.String(1024), nullable=True)
    next_ordinal = db.Column(db.Integer, nullable=False, default=0)
    chapters_count = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now)


class ChapterModel(db.Model):
    __tablename__ = 'chapters'
    __table_args__ = (
        db.Index('idx_book_id_ordinal', 'book_id', 'ordinal', unique=True),
    )

    id = db.Column(db.String(256), primary_key=True)
    book_id = db.Column(db.String(256), nullable=False)
    ordinal = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(1024), nullable=False)
    source = db.Column(db.Text, nullable=True)
    html = db.Column(db.Text, nullable=True)
    version = db.Column(db.Integer, nullable=False, default=0)


class ArticleModel(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.String(256), primary_key=True)
    author = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(1024), nullable=False)
    summary = db.Column(db.String(2048), nullable=True)
    icon = db.Column(db.String(1024), nullable=False)
    is_draft = db.Column(db.Boolean, nullable=False, default=True)
    source = db.Column(db.Text, nullable=True)
    html = db.Column(db.Text, nullable=True)
    create_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now)


ArticleCategories = OrderedDict(
    Python="Python", Java="Java", Golang="Golang", Node="Node")


class ArticleCategoryModel(db.Model):
    __tablename__ = 'post_category'

    book_id = db.Column(db.String(256), primary_key=True)
    category_key = db.Column(db.String(128), primary_key=True)
