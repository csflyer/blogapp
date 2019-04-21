from .. import db
from ..tools.tool import FlashMsg, Log
from . import profile
from ..models import User, Post, Follow
from ..Status import Permission
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, request, current_app, abort
from .forms import ProfileForm


@profile.route('/<id>')
@profile.route('/overview/<id>')
@login_required
def overview(id):
    user = User.query.get_or_404(id)
    fan_count = user.followers.count()
    follower = followed = None
    if current_user.id != user.id:
        follower = True if Follow.query.filter_by(follower_id=user.id, followed_id=current_user.id).first() is not None else False
        followed = True if Follow.query.filter_by(followed_id=user.id, follower_id=current_user.id).first() is not None else False
    return render_template("/profile/profile.html", user=user, overview=True, followed=followed, follower=follower, fan_count=fan_count)


@profile.route('/<id>/posts/')
@login_required
def post(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.created_at.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    follower = followed = None
    if current_user.id != user.id:
        follower = True if Follow.query.filter_by(follower_id=user.id, followed_id=current_user.id).first() is not None else False
        followed = True if Follow.query.filter_by(followed_id=user.id, follower_id=current_user.id).first() is not None else False
    return render_template("/profile/profile.html", user=user, follower=follower,followed=followed,
                           post=True, posts=posts, pagination=pagination)


@profile.route('/edit', methods=['GET', 'POST'])
@login_required
@Permission.Required(Permission.WRITE_ARTICLES)
def edit():
    user = current_user._get_current_object()
    form = ProfileForm(obj=user)
    Log.info('Try to edit profile')
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        FlashMsg.info('您的个人资料已成功修改!')
        return redirect(url_for('profile.overview', id=user.id))
    return render_template("/profile/profile.html", edit=True, form=form, user=current_user)


@profile.route('/unfollow/<id>')
@login_required
@Permission.Required(Permission.FOLLOW)
def unfollow(id):
    user = User.query.get_or_404(id)
    Log.info('Try to Unfollow:{}'.format(user.id))
    follow = Follow.query.filter_by(follower_id=current_user.id,
                                    followed_id=user.id).first()
    if not follow:
        abort(404)
    db.session.delete(follow)
    db.session.commit()
    return redirect(request.referrer)


@profile.route('/follow/<id>')
@login_required
@Permission.Required(Permission.FOLLOW)
def follow(id):
    user = User.query.get_or_404(id)
    Log.info('Try to follow:{}'.format(user.id))
    follow = Follow.query.filter_by(follower_id=current_user.id,
                                    followed_id=user.id).first()
    if follow:
        return redirect(request.referrer)
    new_follow = Follow(follower_id=current_user.id, followed_id=user.id)
    db.session.add(new_follow)
    db.session.commit()
    return redirect(request.referrer)


@profile.route('/<id>/followed/')
@login_required
def followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.filter(Follow.followed_id != user.id).paginate(
        page, per_page=current_app.config['USER_PER_PAGE'], error_out=False
    )
    users = map(lambda follow: follow.followed, pagination.items)
    follower = followed = None
    if current_user.id != user.id:
        follower = True if Follow.query.filter_by(follower_id=user.id, followed_id=current_user.id).first() is not None else False
        followed = True if Follow.query.filter_by(followed_id=user.id, follower_id=current_user.id).first() is not None else False
    return render_template("/profile/profile.html", user=user, follower=follower,followed=followed,
                           ffollowed=True, users=users, pagination=pagination, endpoint='profile.followed')


@profile.route('/<id>/follower/')
@login_required
def follower(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.filter(Follow.follower_id != user.id).paginate(
        page, per_page=current_app.config['USER_PER_PAGE'], error_out=False
    )
    users = map(lambda follow: follow.follower, pagination.items)
    follower = followed = None
    if current_user.id != user.id:
        follower = True if Follow.query.filter_by(follower_id=user.id, followed_id=current_user.id).first() is not None else False
        followed = True if Follow.query.filter_by(followed_id=user.id, follower_id=current_user.id).first() is not None else False
    return render_template("/profile/profile.html", user=user, follower=follower,followed=followed,
                           ffollower=True, users=users, pagination=pagination, endpoint='profile.follower')

