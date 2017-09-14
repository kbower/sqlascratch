from sqlalchemy import *
from sqlalchemy.orm import *
from datetime import date


# if use_ansi=True, this script succeeds
# if False, this script fails

use_ansi = False
#use_ansi = True

engine = create_engine('oracle://kent:kent@localhost:1521/xe', use_ansi=use_ansi, echo=True) 

metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

# a rock has many bugs

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
)

bugs_table = Table("bugs", metadata,
    Column("id", Integer, primary_key=True),
    Column("rockid", Integer, ForeignKey('rocks.id')),
    Column("deathdate", Date),
)

class Rock(object):
    pass
    
class Bug(object):
    pass
    
mapper(Rock, rocks_table, 
    properties={
        'livingbugs': relationship(Bug,
            primaryjoin=and_(
                bugs_table.c.rockid == rocks_table.c.id,
                bugs_table.c.deathdate == None,
            )),
        })

mapper(Bug, bugs_table)

metadata.create_all()
try:
    s = Session()

    r=Rock()
    r.id = 55
    
    b=Bug()
    b.id = 1
    b.rockid = 55
    b.deathdate = date.today()

    s.add(r)
    s.add(b)
    s.commit()

    s = Session()

    rocks = s.query(Rock).options(joinedload('livingbugs')).all()
    if not rocks:
        # When not using ANSI, if 
        #     AND bugs_1.deathdate IS NULL
        # is changed to:
        #     AND bugs_1.deathdate(+) IS NULL
        # then the join is consistent with ANSI join and doesn't fail
        raise Exception("Rock not selected")

    print("Rocks: %r" % rocks)
    print("rocks[0].livingbugs: %r" % rocks[0].livingbugs)

finally:
    metadata.drop_all()


