from dontmoderateme import app, db, models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    """Adds a test user and creates default site settings"""
    db.create_all()


@manager.command
def create_test_user():
    testuser = models.User('test@test.com', 'test', activated=True)
    db.session.add(testuser)
    db.session.commit()

if __name__ == '__main__':
    manager.run()

