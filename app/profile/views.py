from . import profile
from flask_login import login_required
from flask import render_template


@profile.route('/')
@profile.route('/overview')
@login_required
def overview():
    return render_template("/profile/profile.html", overview=True)



@profile.route('/posts')
@login_required
def post():
    return render_template("/profile/profile.html", post=True)


@profile.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    return render_template("/profile/profile.html", edit=True)
