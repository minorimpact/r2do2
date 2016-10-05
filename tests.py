#!/usr/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Task
from datetime import datetime, timedelta

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        u = User(name='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_tasks(self):
        u = User(name='john2', email='john@example.com')
        t1 = Task(name='Task1', mod_date=datetime.utcnow(), create_date=datetime.utcnow(), user=u)
        t2 = Task(name='Task2', mod_date=datetime.utcnow(), create_date=datetime.utcnow(), user=u, blocked_by=[t1])
        db.session.add(u)
        db.session.add(t1)
        db.session.add(t2)
        db.session.commit()
        assert u.tasks is not None
        count = 0
        for t in u.tasks:
            count += 1
        assert count == 2
        count = 0
        for t in u.open_tasks:
            count += 1
        assert count == 1
        t1.done = True
        db.session.commit()
        count = 0
        for t in u.open_tasks:
            count += 1
        assert t.name == 'Task2'

    def test_full_text_search(self):
        u = User(name='john', email='john@example.com')
        t1 = Task(name='Task1', description='search content: foo', mod_date=datetime.utcnow(), create_date=datetime.utcnow(), user=u)
        t2 = Task(name='Task2', description='search content: bar', mod_date=datetime.utcnow(), create_date=datetime.utcnow(), user=u, blocked_by=[t1])
        db.session.add(u)
        db.session.add(t1)
        db.session.add(t2)
        db.session.commit()
        search_results = u.tasks.whoosh_search('foo').all()
        assert len(search_results) == 1
        search_results = u.tasks.whoosh_search('search content:').all()
        assert len(search_results) == 2
        search_results = u.open_tasks.whoosh_search('search content:').all()
        assert len(search_results) == 1

if __name__ == '__main__':
    unittest.main()
