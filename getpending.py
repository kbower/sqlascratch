# Demonstrate what seems incorrect behavior that sqlalchemy uses committed value when 
# looking up relationships within flush

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy import event
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
                    backref='rock')
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


b1 = Bug()
b1.id = 0

rock=Rock()
rock.id = 1
rock.bugs.append(b1)

print "\n\n****merge start\n"
merged = session.merge(rock)
print "\n\n****merge end\n"
session.expire(merged.bugs[0],['rock'])
merged.bugs[0].rock = session.query(Rock).get(merged.bugs[0].rockid)
print "****flush\n"
session.flush()

assert 'rock' in merged.bugs[0].__dict__
print 'merged.bugs[0].rock: %r' % merged.bugs[0].rock

print session.query(Rock).get(1)