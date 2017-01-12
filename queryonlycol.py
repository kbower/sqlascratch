from sqlalchemy import *
from sqlalchemy.orm import *

metadata = MetaData()

users = Table('users', metadata,
    Column('username', String(50), primary_key=True),
    Column('familyname', String(100), primary_key=True),
)

addresses = Table('addresses', metadata,
    Column('username', String(50)),
    Column('familyname', String(100)),
    Column('email', String(50), primary_key=True),

    ForeignKeyConstraint(['username','familyname'],['users.username','users.familyname'],
        deferrable=True, initially='DEFERRED')
)


class BasicEntity(object):
    def __init__(self, **kw):
        for key, value in kw.iteritems():
            setattr(self, key, value)

class User(BasicEntity):
    pass

class Address(BasicEntity):
    pass


mapper(User, users, properties={
    'addresses':relationship(Address, 
        cascade='all,delete-orphan', passive_updates=False,
        backref=backref('user',passive_updates=True))
})
mapper(Address, addresses)

e = create_engine("sqlite://", echo=True)
metadata.create_all(e)

sess = Session(e)
u1 = User(username='jack', familyname='brown')
sess.add(u1)
u1 = User(username='jill', familyname='brown')
sess.add(u1)
u1 = User(username='bob', familyname='brown')
sess.add(u1)
u1 = User(username='jack', familyname='smith')
sess.add(u1)
sess.commit()


import pdb; pdb.set_trace()

vals = sess.query(User.username).distinct().all()




