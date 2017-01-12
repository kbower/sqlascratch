from sqlalchemy import *
from sqlalchemy.orm import *

m=MetaData()

table_a=Table('a', m,
    Column('id', Integer, primary_key=True)
    )    

### this works    
#table_a.append_column(Column("cola", Integer))
#table_a.append_column(Column("colb", Integer))

### this doesn't
table_a.columns.extend(
    [
    (Column("cola", Integer)),
    (Column("colb", Integer))
    ]
)

class A(object):
    pass

mapper(A, table_a)

print Session().query(A)

