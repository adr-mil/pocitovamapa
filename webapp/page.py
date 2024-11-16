import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('page', __name__)

@bp.route('/')
def page():
    return render_template("page.html")
