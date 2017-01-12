from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True) 
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
#    Column("bugid", Integer, ForeignKey('bugs.id')),
    Column("bugid", Integer),
)

bugs_table = Table("bugs", metadata,
    Column("id", Integer, primary_key=True)
)

class Rock(object):
    pass
    
class Bug(object):
    pass
    

mapper(Rock, rocks_table,
    allow_partial_pks=False,
    properties={'bug': relationship(Bug,
                    cascade='refresh-expire,expunge',
                    primaryjoin=rocks_table.c.bugid==bugs_table.c.id,
                    foreign_keys=[rocks_table.c.bugid]
                    ),
                })    

mapper(Bug, bugs_table)

metadata.create_all()

session = Session()

persistentbug=Bug()
persistentbug.id = 0
session.add(persistentbug)
session.commit()

session = Session()

rock=Rock()
rock.id = 0
rock.bug = session.query(Bug).get(0)
session.add(rock)
session.flush()

session.delete(rock)
session.flush()




