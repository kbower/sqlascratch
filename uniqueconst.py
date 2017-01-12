from sqlalchemy import *
engine = create_engine('sqlite:///', echo=True) 
engine = create_engine('oracle://kent:kent@localhost:1521/xe',echo=True)
metadata = MetaData(engine)

##############################################
table=Table("sometable", metadata, 
    Column("id_a", Unicode(255), primary_key=True), 
    Column("id_b", Unicode(255)), 
#    Index('id_b'),
    UniqueConstraint('id_a','id_b'),
)

# passes:
#assert len(table.indexes) == 1
# passes:
assert any(type(a) == UniqueConstraint for a in table.constraints)

##############################################
tableb=Table("sometableb", metadata, 
    Column("id_a", Unicode(255), primary_key=True), 
    Column("id_b", Unicode(255)), 
)
#Index('tablebindex', tableb.c.id_b)
UniqueConstraint('tablebconstraint', tableb.c.id_a, tableb.c.id_b)

# passes:
#assert len(tableb.indexes) == 1
# fails:
#assert any(type(a) == UniqueConstraint for a in tableb.constraints)


metadata.create_all()

