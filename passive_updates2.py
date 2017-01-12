from sqlalchemy import *
from sqlalchemy.orm import *

metadata = MetaData()

families = Table('families', metadata,
    Column('familyname', String(100), primary_key=True))

users = Table('users', metadata,
    Column('username', String(50), primary_key=True),
    Column('familyname', String(100), 
        ForeignKey('families.familyname'), primary_key=True),
)

addresses = Table('addresses', metadata,
    Column('username', String(50)),
    Column('familyname', String(100)),
    Column('email', String(50), primary_key=True),

    ForeignKeyConstraint(['username','familyname'],['users.username','users.familyname'],
        deferrable=True, initially='DEFERRED'),
)

class BasicEntity(object):
    def __init__(self, **kw):
        for key, value in kw.iteritems():
            setattr(self, key, value)

class Family(BasicEntity):
    pass
    
class User(BasicEntity):
    pass

class Address(BasicEntity):
    pass

mapper(Family, families, properties={
    'members': relationship(User,
        cascade='all,delete-orphan',
        single_parent=True)
})

mapper(User, users, properties={
    'addresses':relationship(Address, 
        cascade='all,delete-orphan', passive_updates=False,
        backref=backref('user',passive_updates=True))
})
mapper(Address, addresses)

e = create_engine("sqlite://", echo=True)
metadata.create_all(e)
sess = Session(e)

f1 = Family(familyname='brown')
u1 = User(username='jack')
f1.members = [u1]
u1.addresses = [Address(email='jack1@j.com'), Address(email='jack2@j.net')]
sess.add(f1)
sess.commit()

f2 = Family(familyname='johnson')
sess.add(f2)
f2.members = [u1]

#u1.username='ed'

sess.commit()

assert sess.execute("select familyname from addresses").fetchall() == [
    ("johnson",),
    ("johnson",)]

