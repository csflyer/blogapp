import os
from app.models import User, Role, Post, Follow, ClassifyTag, Comment, ArticleTag
from app import create_app, db
from app.tools.send_mail import send_mail
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.environ.get('BLOG_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Follow=Follow, ClassifyTag=ClassifyTag,
                Comment=Comment, ArticleTag=ArticleTag, send_mail=send_mail)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
