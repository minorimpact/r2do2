import re
from app import db, app
from hashlib import md5
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event

import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    # apt-get install python-pip
    # pip install flask-whooshalchemy
    import flask.ext.whooshalchemy as whooshalchemy

tags = db.Table('tags',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('name', db.String(50)),
    db.Column('object_type', db.String(50)),
    db.Column('object_id', db.Integer),
)
blocked = db.Table('blocked',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('blocked_task_id', db.Integer, db.ForeignKey('task.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(25), index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    # This doesn't work with pagination, so I recreated it as an object property that returns a
    # query.  Shitty hack?
    #tasks = db.relationship('Task')
    password = db.Column(db.String(255))
    description = db.Column(db.String(255))
    test = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)

    @property
    def tasks(self):
        return Task.query.filter(Task.user_id==self.id, Task.done==False).order_by(Task.name)

    @property
    def open_tasks(self):
        return self.tasks.filter(~Task.blocked_by.any())

    #@property
    def is_authenticated(self):
        return True

    #@property
    def is_active(self):
        return True
    
    #@property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    @staticmethod
    def make_unique_name(name):
        if User.query.filter_by(name=name).first() is None:
            return name
        version = 2
        while True:
            new_name = name + str(version)
            if User.query.filter_by(name=new_name).first() is None:
                break
            version += 1
        return new_name

    @staticmethod
    def make_valid_name(name):
        return re.sub('[^a-zA-Z0-9_\.]', '', name)


class Task(db.Model):
    __searchable__ = ['name', 'description']

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(255))
    create_date = db.Column(db.DateTime)
    done = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime)
    mod_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    blocks = db.relationship('Task',
                              secondary = blocked,
                              primaryjoin = (blocked.c.task_id==id),
                              secondaryjoin = (blocked.c.blocked_task_id==id))
    blocked_by = db.relationship('Task',
                              secondary = blocked,
                              primaryjoin = (blocked.c.blocked_task_id==id),
                              secondaryjoin = (blocked.c.task_id==id))

    #def tags(self):
        #return tags.query.filter(tags.object_id==self.id, tags.object_type=self.__class__.__name__ ).order_by(tags.name)

    #def addTags(self, tags):
        #for t in tags:
            #self.addTag(t)

    @hybrid_property
    def is_blocked(self):
        #if self.blocked_by is not None and len(self.blocked_by) > 0:
        if len(self.blocked_by) > 0:
            return True 
        return False

    def __repr__(self):
        return '<Task %r>' % (self.name)

@event.listens_for(Task, 'after_update')
def after_update_task(mapper, connection, target):
    if target.done == True:
        connection.execute(blocked.delete().where(blocked.c.task_id==target.id))
        connection.execute(blocked.delete().where(blocked.c.blocked_task_id==target.id))

@event.listens_for(Task, 'before_delete')
def before_delete_task(mapper, connection, target):
    connection.execute(blocked.delete().where(blocked.c.task_id==target.id))
    connection.execute(blocked.delete().where(blocked.c.blocked_task_id==target.id))

if enable_search:
    whooshalchemy.whoosh_index(app, Task)

