# pylint: disable=all

from flask import request, jsonify, Blueprint

import markdown

blueprint = Blueprint("preview", __name__, url_prefix='/preview')


@blueprint.route("/markdown.json", methods=["POST"])
def markdown_to_html():
    content = (request.form.get('content') or '').strip()
    return jsonify({
        "content": markdown.markdown(content)
    })
