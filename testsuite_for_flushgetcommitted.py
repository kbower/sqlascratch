# m bayer sent this to demonstrate why during flush the orm needs to use committed value when looking up 
# relationships


from sqlalchemy import *
from sqlalchemy.orm import *

metadata = MetaData()
users = Table('users', metadata,
    Column('username', String(50), primary_key=True),
    Column('fullname', String(100)))

addresses = Table('addresses', metadata,
    Column('email', String(50), primary_key=True),
    Column('username', String(50), 
                    ForeignKey('users.username')))


class BasicEntity(object):
    def __init__(self, **kw):
        for key, value in kw.iteritems():
            setattr(self, key, value)

class User(BasicEntity):
    pass

class Address(BasicEntity):
    pass

class UserAgent(MapperExtension):
    def before_update(self, mapper, connection, instance):
        pass

mapper(User, users,  extension=UserAgent(), properties={
    'addresses':relationship(Address, passive_updates=False)
})
mapper(Address, addresses)

e = create_engine("sqlite://", echo=True)
metadata.create_all(e)

sess = Session(e)
u1 = User(username='jack', fullname='jack')
u1.addresses.append(Address(email='jack1'))
u1.addresses.append(Address(email='jack2'))
sess.add(u1)
sess.commit()

u1.username = 'ed'
sess.commit()

assert sess.execute("select username from addresses").fetchall() == [
    ("ed",),
    ("ed",)]







