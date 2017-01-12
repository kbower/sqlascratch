from sqlalchemy import *
from sqlalchemy.sql import text

engine = create_engine('oracle://kent:kent@localhost:1521/xe',echo=True)
metadata = MetaData(engine)

table=Table("sometable", metadata, 
    Column("id_a", Unicode(255), primary_key=True), 
    Column("id_b", Unicode(255)), 
    Column("id_c", Unicode(255)),  
)
Index('tableind', table.c.id_b, table.c.id_c)

# create
metadata.create_all()

primaryconsname = engine.execute(
   text("ALTER TABLE SOMETABLE ADD CONSTRAINT SOME_U_CONST UNIQUE (ID_B)"))

try:
    # round trip, create from reflection
    mirror = MetaData(engine)
    mirror.reflect(only=[table.name])
    metadata.drop_all()
    mirror.create_all()

    # inspect the reflected creation
    inspect = MetaData(engine)
    inspect.reflect()

    def obj_definition(obj):
        return (obj.__class__, tuple([c.name for c in obj.columns]), getattr(obj, 'unique', None))

    reflectedtable = inspect.tables[table.name]

    # make a dictionary of the reflected objects:
    reflected = dict([(obj_definition(i), i) for i in reflectedtable.indexes | reflectedtable.constraints])
    

    # Error if not in dict
    assert (PrimaryKeyConstraint, ('id_a',), None) in reflected
    assert (Index, ('id_b','id_c',), False) in reflected
    assert len(reflectedtable.constraints) == 1

    assert len(reflectedtable.indexes) == 2

finally:
    metadata.drop_all()
