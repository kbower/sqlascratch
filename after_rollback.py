from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy import event
from sqlalchemy import __version__ as sqlaversion
print("sqlalchemy %s" % sqlaversion)

triggered_properly = False

engine = create_engine('sqlite:///', echo=True) 

maker = sessionmaker(autoflush=True, autocommit=False, bind=engine)
DBSession = scoped_session(maker)

@event.listens_for(DBSession, 'after_rollback')
def receive_after_rollback(session):
    print("after_rollback triggered")
    global triggered_properly
    triggered_properly = True

@event.listens_for(DBSession, 'after_soft_rollback')
def receive_after_rollback(session, prev_tran):
    print("after_soft_rollback triggered")
    global triggered_properly
    triggered_properly = True

@event.listens_for(DBSession, "after_transaction_end")
def receive_after_transaction_end(session, transaction):
    print("after_transaction_end triggered")
    import pdb; pdb.set_trace()
    global triggered_properly
    triggered_properly = True

if sqlaversion >= '2':
    metadata = MetaData()
    from sqlalchemy.orm import registry
    mapper_reg = registry()
    mapper = mapper_reg.map_imperatively
else:
    metadata = MetaData(engine)
table=Table("sites", metadata, 
    Column("siteid", Unicode(255), primary_key=True), 
    Column("name", Unicode(255)), 
)

class Site(object):
    pass


mapper(Site, table)    

if sqlaversion >= '2':
    metadata.create_all(engine)
else:
    metadata.create_all()

DBSession.query(Site).all()

#DBSession.rollback()
DBSession.close()

assert(triggered_properly)

print("exiting successfully")