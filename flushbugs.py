# Demonstrate what seems incorrect behavior that sqlalchemy uses committed value when 
# looking up relationships within flush

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
    Column("rockid", Integer, ForeignKey('rocks.id'),),
)

class Rock(object):
    def __repr__(self):
        return '<Rock: id=[%s]>' % self.__dict__.get('id')
    
class Bug(object):
    def __repr__(self):
        return '<Bug: id=[%s]>' % self.__dict__.get('id')
        
    def printstate(self, msg):
        print "\n******* %s: rockid=[%s] rock object: %r\n" % (msg, self.__dict__.get('rockid'), self.rock)
    

class BugAgent(MapperExtension):
    def before_update(self, mapper, connection, instance):
        instance.printstate("During flush")
        session.expire(instance, ['rock'])

mapper(Rock, rocks_table,
    properties={'bugs': relationship(Bug,
                    cascade='all,delete-orphan', 
                    single_parent=True,
                    lazy=False,
                    backref='rock')
                })    

mapper(Bug, bugs_table, extension=BugAgent())

metadata.create_all()

session = Session()


# add a rock and bug
rock=Rock()
rock.id = 0
bug=Bug()
bug.id = 0
rock.bugs.append(bug)
session.add(rock)

# add another rock and bug
rock=Rock()
rock.id = 1
bug=Bug()
bug.id = 1
rock.bugs.append(bug)
session.add(rock)

session.commit()
session.expunge_all()

# later... new session
session = Session()

b1 = session.query(Bug).get(1)

b1.printstate("Before move")

# Move bug to another rock...
b1.rockid = 0
session.expire(b1, ['rock'])

session.flush()

b1.printstate("After flush")
