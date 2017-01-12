# demo for "sqlalchemy.orm.exc.FlushError: Can't update table using NULL for primary key value"
# when no SQL statement will really be needed and allow_partial_pks is True
from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True)

metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
session = Session()

mytable = Table("notrueprimarykey", metadata,
    Column("a", Unicode, primary_key=True),
    Column("b", Unicode, primary_key=True),
    Column("data", Unicode)
)

class Object(object):
    def __init__(self, **kw):
        for key, value in kw.iteritems():
            setattr(self, key, value)

mapper(Object, mytable, allow_partial_pks=True)

engine.execute("""
CREATE TABLE notrueprimarykey (
    a VARCHAR NOT NULL,
    b VARCHAR,
    data VARCHAR,
    UNIQUE (a, b)
)""")

try:
    engine.execute(mytable.insert().values(a=u'1', b=None, data=u'data'))
    obj = Object(a=u'1',b=None)    
    merged = session.merge(obj)

    session.flush()
finally:
    engine.execute("DROP TABLE notrueprimarykey")
