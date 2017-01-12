# attributes.PASSIVE_NO_RESULT as old value when merging

from sqlalchemy import *
from sqlalchemy.orm import *

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

class Rock(object):
    def __repr__(self):
        return '<Rock: id=[%s]>' % self.__dict__.get('id')
    
class Bug(object):
    def __repr__(self):
        return '<Bug: id=[%s]>' % self.__dict__.get('id')
        
mapper(Rock, rocks_table,
    properties={'bug': relationship(Bug,
                    cascade='all,delete-orphan',
                    load_on_pending=True,
                    uselist=False)
                })

#mapper(Bug, bugs_table)

metadata.create_all()

session = Session()

# create a transient rock with None bug
r = Rock()
r.bug = None

session.merge(r)
