# pylint: disable=all

from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/codehole.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True

with app.app_context():
    from codehole.db import db
    db.create_all()

from codehole.views import book, chapter, article, index
app.register_blueprint(article.blueprint)
app.register_blueprint(book.blueprint)
app.register_blueprint(chapter.blueprint)
app.register_blueprint(index.blueprint)
