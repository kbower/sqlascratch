from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('oracle://arc:arc@localhost:1521/xe',echo=True)
metadata = MetaData(engine)
session = sessionmaker(bind=engine)()

class SaClass(object):
    pass

mapper(SaClass, Table("atable", metadata, 
    Column("_underscorecolumn", Unicode(255), primary_key=True)
))
metadata.create_all()

#engine.dialect.supports_unicode_binds = False

try:
    session.query(SaClass).filter(SaClass._underscorecolumn==u'value').all()
finally:
    metadata.drop_all()
