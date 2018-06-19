# pylint: disable=all

import os
from flask import Flask
app = Flask(__name__)
dbfile = os.path.expanduser('~') + '/data/codehole.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['TEMPLATES_AUTO_RELOAD'] = True

with app.app_context():
    from codehole.db import db
    db.create_all()

from codehole.views import book, article, preview, index
app.register_blueprint(article.blueprint)
app.register_blueprint(book.blueprint)
app.register_blueprint(preview.blueprint)
app.register_blueprint(index.blueprint)
