from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('postgresql://salespylot:salespylot@localhost:5444/salespylottest',echo=True)

maker = sessionmaker(autoflush=True, autocommit=False)
DBSession = scoped_session(maker)

metadata = MetaData(engine)
table=Table("sometable", metadata, 
    Column("id_a", Unicode(255), primary_key=True), 
    Column("id_b", Unicode(255)), 
)

class SomeClass(object):
    pass

mapper(SomeClass, table,
    properties = {
        'inefficient_subselect': 
            # suppose this deferred column property isn't very efficient
            column_property(
                (table.c.id_a + table.c.id_b).label('inefficient_subselect'),
                deferred=True)
    }
)    

metadata.create_all()
try:
    session = DBSession()
    obj = SomeClass()
    obj.id_a = 'PK1'
    session.add(obj)
    session.flush()
    session.commit()
    DBSession.remove()
    session = DBSession()
    session.begin_nested()
    o = session.query(SomeClass).get('PK1')
    o.id_b = '01'
    #o.inefficient_subselect
    session.flush()
    if 'inefficient_subselect' in o._sa_instance_state.expired_attributes:
        raise Exception("inefficient_subselect wasn't loaded before (and is "
            "deferred), so probably shouldn't be in expired_attributes")
    session.rollback()
    # if "raise" is removed, this loads the deferred column_property:
    o.id_a

finally:
    DBSession.remove()
    metadata.drop_all()
