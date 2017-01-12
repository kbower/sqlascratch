# coding: utf-8

from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('oracle://arc:arc@localhost:1521/xe',echo=True)
metadata = MetaData(engine)

t1 = Table("t1", metadata, 
    Column(u'méil', Integer, primary_key=True)
)
t2 = Table("t2", metadata, 
    Column(u'méil', String(50), primary_key=True)
)

metadata.create_all()

try:
    # passes
    engine.execute(
        t2.select().where(t2.c[u'méil']=='value')
    )
    # fails: ORA-01036: illegal variable name/number
    engine.execute(
        t1.select().where(t1.c[u'méil']==5)
    )
finally:
    metadata.drop_all()

