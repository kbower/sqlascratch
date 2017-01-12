from sqlalchemy import *
from sqlalchemy.orm import *

#engine = create_engine('oracle://kent:kent@localhost:1521/xe',echo=True)
engine = create_engine("oracle://kent:kent@localhost/xe")


m=MetaData(engine)

table_a=Table('a', m,
    Column('id', Integer, primary_key=True),
    Column('notes', Unicode(50))    
    )    

class A(object):
    pass

mapper(A, table_a)

metadata.create_all()
try:
    pass
finally:
    metadata.drop_all()


