from sqlalchemy import *
from sqlalchemy.orm import *

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
    

mapper(Rock, rocks_table,
    properties={'bugs': relationship(Bug,
                    cascade='all,delete-orphan', 
                    single_parent=True,
                    lazy=False,
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
currentobjects = session.query(Rock).all()

mergeda = session.merge(rocka)

assert mergeda.bugs[0].rock is mergeda
assert mergeda.bugs[1].rock is mergeda

mergedb = session.merge(rockb)

# Same tests as before:
assert mergeda.bugs[0].rock is mergeda
# now, mergeda.bugs[1].rock is None and this fails: ############
assert mergeda.bugs[1].rock is mergeda

# flush incorrectly DELETES bug
session.flush()

