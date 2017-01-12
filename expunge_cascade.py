from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.util import has_identity

engine = create_engine('sqlite:///', echo=True)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
)

bugs_table = Table("bugs", metadata,
    Column("id", Integer, primary_key=True),
    Column("rockid", Integer, ForeignKey('rocks.id'),),
)

class Rock(object):
    def __repr__(self):
        return '<Rock@%d: id=[%s] in session:[%s] has_identity[%s]>' % (id(self), self.__dict__.get('id'), self in session, has_identity(self))
    
class Bug(object):
    def __repr__(self):
        return '<Bug@%d: id=[%s] rockid[%s] with rock[%s]>' % (id(self), self.__dict__.get('id'), self.__dict__.get('rockid'), self.__dict__.get('rock','not set'))
    

mapper(Rock, rocks_table,
    properties={'bugs': relationship(Bug,
                    cascade='all,delete-orphan', 
                    backref=backref('rock',cascade='refresh-expire,expunge'))
                })    

mapper(Bug, bugs_table)


metadata.create_all()

session = Session()


# add a rock and bug
rock=Rock()
rock.id = 0
bug=Bug()
bug.id = 0
rock.bugs.append(bug)
session.add(rock)

session.commit()

# later... new session
session = Session()
rock = session.query(Rock).get(0)
rock.bugs.append(Bug())

assert rock in session

rock.bugs = []

assert rock in session
