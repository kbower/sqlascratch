from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True) 
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
    Column("primarybugid", Integer, ForeignKey('bugs.id')),
    Column("secondarybugid", Integer, ForeignKey('bugs.id'))
)

bugs_table = Table("bugs", metadata,
    Column("id", Integer, primary_key=True)
)

class Rock(object):
    pass
    
class Bug(object):
    pass
    

mapper(Rock, rocks_table,
    properties={'primarybug': relationship(Bug,
                    cascade='refresh-expire,expunge',
                    #uselist=False,
                    primaryjoin=rocks_table.c.primarybugid==bugs_table.c.id,
                    #foreign_keys=[bugs_table.c.id]
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
rock.primarybug = session.query(Bug).get(0)
session.add(rock)
session.flush()





