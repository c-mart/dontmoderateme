from dontmoderateme import app, db, models
from flask_script import Manager

manager = Manager(app)


@manager.command
def init_db():
    """Adds a test user and creates default site settings"""
    db.create_all()
    testuser = models.User('test@test.com', 'test', activated=True)
    db.session.add(testuser)
    db.session.commit()

if __name__ == '__main__':
    manager.run()

