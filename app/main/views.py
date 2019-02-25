from . import main
from flask import render_template,session, request, flash, redirect, url_for, get_flashed_messages


@main.route('/')
def index():
    return render_template('main/index.html')


