from . import main
from flask_login import login_required
from flask import render_template,session, request, flash, redirect, url_for, get_flashed_messages


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/search')
def search():
    pass


@main.route('/profile')
@main.route('/profile/overview')
@login_required
def profile():
    pass



