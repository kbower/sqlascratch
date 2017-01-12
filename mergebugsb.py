from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm.interfaces import AttributeExtension

engine = create_engine('sqlite:///', echo=True) 
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
)

bugs_table = Table("bugs", metadata,
    Column("rockid", Integer, ForeignKey('rocks.id'), primary_key=True,),
    Column("id", Integer, primary_key=True),
)

class Rock(object):
    pass
    
class Bug(object):
    pass
    

class BugsAttribute(AttributeExtension):
    def append(self, state, bug, starter):
        if 'rock' in bug.__dict__:
            currentrock = bug.rock
            if 'bugs' in currentrock.__dict__ and \
               currentrock is not state.obj():
                print "EXPIRE HERE"
        else:
            print 'rock not populated'
        return bug

mapper(Rock, rocks_table,
    properties={'bugs': relationship(Bug,
                    cascade='all,delete-orphan', 
                    single_parent=True,
                    lazy=False,
                    extension=BugsAttribute(),
                    backref='rock')
                })    

mapper(Bug, bugs_table,
    allow_partial_pks=False)

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

# later... new session, we are moving second bug to the first rock using merge()
session = Session()

rocka=Rock()
rocka.id = 0

buga=Bug()
buga.id=0
buga.rockid=0
bugb=Bug()
bugb.id=1
bugb.rockid=1

rocka.bugs = [buga,bugb]

rockb=Rock()
rockb.id = 1
rockb.bugs = []

# NOTE: if this line is commented out, the behavior changes completely (seems to work)
import pdb; pdb.set_trace()
currentobjects = session.query(Rock).all()

allbugs = session.query(Bug).all()
r1 = session.query(Rock).get(0)
r1.bugs = allbugs

assert r1.bugs[0].rock is r1
assert r1.bugs[1].rock is r1

session.flush()
#session.expire_all()

r2 = session.query(Rock).get(1)
r2.bugs = []

assert r1.bugs[0].rock is r1
assert r1.bugs[1].rock is r1

# no-op
session.flush()