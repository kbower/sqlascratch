# coding: utf-8
from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('oracle://arc:arc@localhost:1521/xe',echo=True)
metadata = MetaData(engine)

engine.dialect.convert_unicode = True

om = Table("ordermarkers", metadata, 
    Column("markerid", Unicode(255), primary_key=True),
    Column("description", Unicode(255))
)
#metadata.create_all()

try:
    s = om.update().values(description=bindparam('b_desc')).where(om.c.markerid==bindparam('b_mid'))
    c = engine.connect()
    c.execute(s, b_desc=u'new desc', b_mid=u'KB')

finally:
#    metadata.drop_all()
    pass