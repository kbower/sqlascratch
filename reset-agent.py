# ticket #9772
from sqlalchemy import *
from sqlalchemy.orm import *
from zope.sqlalchemy import ZopeTransactionExtension
from zope.sqlalchemy import mark_changed
from sqlalchemy import event
import transaction

from sqlalchemy import __version__
print "sqlalchemy %s" % __version__

def reset_db_session_for_postgres(connection):
    print "reset_db_session_for_postgres at %x" % id(connection)
    connection.info

engine = create_engine('postgresql://salespylot:salespylot@localhost:5444/salespylottest',echo=True)
event.listen(engine, 'rollback', reset_db_session_for_postgres)

conn = engine.connect()
conn._has_events = True

maker = sessionmaker(autoflush=True, autocommit=False, extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)
DBSession.configure(bind=conn)


metadata = MetaData(engine)
table=Table("sites", metadata, 
    Column("siteid", Unicode(255), primary_key=True), 
    Column("name", Unicode(255)), 
)

class Site(object):
    pass

mapper(Site, table)    

DBSession.query(Site).all()
DBSession.begin_nested()
DBSession.query(Site).all()
transaction.doom()
transaction.begin()
DBSession.query(Site).all()
mark_changed(DBSession())
transaction.commit()
DBSession.query(Site).all()
conn.close()
transaction.abort()
