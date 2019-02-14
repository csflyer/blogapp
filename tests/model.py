# @Time : 2019-02-13 14:50
# @Author : Crazyliu
# @File : model.py.py


import unittest
from app import db
from app.models import User, Role, Post, Follow, ClassifyTag, Comment, ArticleTag


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_1_user_role(self):
        admin_role = Role(name='admin')
        admin_user = User(name='admin', role=admin_role)
        test_user = User(name='test', role=admin_role)
        db.session.add_all([admin_role, admin_user, test_user])
        db.session.commit()

        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User.query.filter_by(name='admin').first()
        self.assertFalse(admin_role is None)
        self.assertFalse(admin_user is None)
        self.assertTrue(admin_role.users.count() == 2)
        self.assertTrue(admin_user.role == admin_role)
        self.assertTrue(admin_role.users.filter_by(name='admin').first() == admin_user)
        db.session.delete(test_user)
        db.session.commit()

    def test_2_user_post(self):
        admin_user = User.query.first()
        admin_post = Post(title='admin', user=admin_user)
        test_post = Post(title='test', user=admin_user)
        db.session.add_all([admin_post, test_post])
        db.session.commit()

        admin_user = User.query.first()
        admin_post = Post.query.filter_by(title='admin').first()
        self.assertFalse(admin_post is None)
        self.assertTrue(admin_user.posts.count() == 2)
        self.assertTrue(admin_post.user == admin_user)
        self.assertTrue(admin_user.posts.filter_by(title='admin').first() == admin_post)
        db.session.delete(test_post)
        db.session.commit()

    def test_3_user_classify_tag(self):
        admin_user = User.query.first()
        admin_tag = ClassifyTag(name='admin', user=admin_user)
        test_tag = ClassifyTag(name='test', user=admin_user)
        db.session.add_all([admin_tag, test_tag])
        db.session.commit()

        admin_user = User.query.first()
        admin_tag = ClassifyTag.query.filter_by(name='admin').first()
        self.assertFalse(admin_tag is None)
        self.assertTrue(admin_user.classifytags.count() == 2)
        self.assertTrue(admin_tag.user == admin_user)
        self.assertTrue(admin_user.classifytags.filter_by(name='admin').first() == admin_tag)
        db.session.delete(test_tag)
        db.session.commit()

    def test_4_user_comment(self):
        admin_user = User.query.first()
        admin_post = Post.query.first()
        admin_comment = Comment(content='admin', floor=2, user=admin_user, post=admin_post)
        test_comment = Comment(content='test', floor=3, user=admin_user, post=admin_post)
        db.session.add_all([admin_comment, test_comment])
        db.session.commit()

        admin_user = User.query.first()
        admin_comment = Comment.query.filter_by(content='admin').first()
        self.assertFalse(admin_comment is None)
        self.assertTrue(admin_user.comments.count() == 2)
        self.assertTrue(admin_comment.user == admin_user)
        self.assertTrue(admin_user.comments.filter_by(content='admin').first() == admin_comment)

    def test_5_post_comment(self):
        admin_post = Post.query.first()
        test_





