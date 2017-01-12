from sqlalchemy import *
from sqlalchemy.sql import text

engine = create_engine('oracle://kent:kent@localhost:1521/xe',echo=True)
metadata = MetaData(engine)

table=Table("sometable", metadata, 
    Column("id_a", Unicode(255), primary_key=True), 
    Column("id_b", Unicode(255), primary_key=True, unique=True), 
    Column("group", Unicode(255), primary_key=True),  
    Column("col", Unicode(255)), 
    UniqueConstraint('col','group'),
)

normalind = Index('tableind', table.c.id_b, table.c.group) # "group" is a keyword, so lower case

# create
metadata.create_all()
try:
    # round trip, create from reflection
    mirror = MetaData(engine)
    mirror.reflect()
    metadata.drop_all()
    mirror.create_all()

    # inspect the reflected creation
    inspect = MetaData(engine)
    inspect.reflect()

    def obj_definition(obj):
        return (obj.__class__, tuple([c.name for c in obj.columns]), getattr(obj, 'unique', None))

    # find what the primary k constraint name should be
    primaryconsname = engine.execute(
       text("""SELECT constraint_name
           FROM all_constraints
           WHERE table_name = :table_name
           AND owner = :owner
           AND constraint_type = 'P' """),
       table_name=table.name.upper(), 
       owner=engine.url.username.upper()).fetchall()[0][0]

    reflectedtable = inspect.tables[table.name]

    # make a dictionary of the reflected objects:
    reflected = dict([(obj_definition(i), i) for i in reflectedtable.indexes | reflectedtable.constraints])

    # assert we got primary key constraint and its name, Error if not in dict
    assert reflected[(PrimaryKeyConstraint, ('id_a','id_b','group',), None)].name.upper() == primaryconsname.upper()
    # Error if not in dict
    assert reflected[(Index, ('id_b','group',), False)].name == normalind.name
    assert (Index, ('id_b',), True) in reflected
    assert (Index, ('col','group',), True) in reflected
    assert len(reflectedtable.constraints) == 1
    assert len(reflectedtable.indexes) == 3

finally:
    metadata.drop_all()
