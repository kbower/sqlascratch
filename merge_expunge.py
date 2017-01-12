from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm import attributes

engine = create_engine('sqlite:///', echo=True)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
)

bugs_table = Table("bugs", metadata,
    Column("id", Integer, primary_key=True),
    Column("rockid", Integer, ForeignKey('rocks.id')),
)

class Object(object):
    def __init__(self, **attrs):
        self.__dict__.update(attrs)

class Rock(Object):
    def __repr__(self):
        return '<Rock: id=[%s]>' % self.__dict__.get('id')
    
class Bug(Object):
    def __repr__(self):
        return '<Bug: id=[%s]>' % self.__dict__.get('id')
        
mapper(Rock, rocks_table,
    properties={'bugs': relationship(Bug,
                    cascade='all,delete-orphan',
                    backref=backref('rock',cascade='refresh-expire,expunge'))
                })    

mapper(Bug, bugs_table)

metadata.create_all()
try:
    session = Session()
    r = Rock(id=1)
    r.bugs=[Bug(id=1)]
    session.add(r)
    session.commit()

    session = Session()
    r = Rock(id=1)
    r.bugs=[]
    merged = session.merge(r)
    session.expunge(merged)
    # if merged is now detached, should flush() still delete Bug?
    session.flush()
    # should history still have deleted Bug?
    print "\n############\nadd: %r\nunchanged: %r\ndelete: %r\n" % attributes.get_history(merged, 'bugs')
    
    # this only fails if the backref 'rock' is present in relationship
    session.add(merged)

finally:
    metadata.drop_all()
    