from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True) 
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
    Column("rocktype", Unicode),
)


class Rock(object):
    pass
    

mapper(Rock, rocks_table)

metadata.create_all()

session = Session()

rock=Rock()
rock.id = 3
rock.rocktype = u'MOSS'
session.add(rock)

rock=Rock()
rock.id = 9
rock.rocktype = u'HARD'
session.add(rock)


print(session.query(func.sum(Rock.id)).scalar())





