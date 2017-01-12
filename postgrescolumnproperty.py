from sqlalchemy import *
from sqlalchemy.orm import *

#engine = create_engine('oracle://kent:kent@localhost:1521/xe',echo=True)
engine = create_engine('postgresql://salespylot:salespylot@localhost:5444/salespylottest',echo=True)

metadata = MetaData(engine)
table=Table("sometable", metadata, 
    Column("id_a", Unicode(255), primary_key=True), 
    Column("id_b", Unicode(255)), 
)

class SomeClass(object):
    pass

mapper(SomeClass, table,
    properties = {
        'fullid': 
            column_property((table.c.id_a + table.c.id_b).label('fullid'))
    }
)    

metadata.create_all()
try:
    session = Session()
    session.query(SomeClass).filter(SomeClass.fullid==None).all()

finally:
    metadata.drop_all()
