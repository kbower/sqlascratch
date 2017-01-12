from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True) 
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
    Column("rocktype", Unicode),
)

bugs_table = Table("bugs", metadata,
    Column("id", Integer, primary_key=True),
    Column("rocktype", Unicode, primary_key=True),
)

class Rock(object):
    pass
    
class Bug(object):
    pass
    

mapper(Rock, rocks_table,
    properties={'bugs': relationship(Bug,
                    # really many to many with no secondary table
                    passive_deletes='all',
                    cascade='save-update,refresh-expire,expunge',
                    primaryjoin=rocks_table.c.rocktype==bugs_table.c.rocktype,
                    foreign_keys=[bugs_table.c.rocktype]
                    ),
                })    

mapper(Bug, bugs_table,
    allow_partial_pks=True)

metadata.create_all()

session = Session()


rock=Rock()
rock.id = 0
rock.rocktype = 'MOSS'

bug=Bug()
bug.id = 0

rock.bugs.append(bug)

session.add(rock)

session.flush()


# later...
session.delete(bug)
session.flush()





