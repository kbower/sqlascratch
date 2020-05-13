# ticket #9772, see also reset-agent.py script, which is closer to jobreport.py
# script sent to m.bayer in https://groups.google.com/forum/?utm_medium=email&utm_source=footer#!msg/sqlalchemy/Lit5HWFiC0U/y6nE-uksBAAJ
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy import event
from sqlalchemy import __version__

print "\n## sqlalchemy %s\n" % __version__

def do_some_info_reset(connection):
    print("## ## do_some_info_reset on %x ## ##" % id(connection))
    # access connection:
    connection.info

pg_url = 'postgresql://salespylot:salespylot@localhost:5444/salespylottest'

engine = create_engine(pg_url, echo=True)
event.listen(engine, 'rollback', do_some_info_reset)

conn = engine.connect()

maker = sessionmaker(autoflush=True, autocommit=False)
DBSession = scoped_session(maker)
DBSession.configure(bind=conn)

metadata = MetaData(engine)
# map a system postgres table for demo purposes:
table=Table("pg_language", metadata, 
    Column("lanname", Unicode(255), primary_key=True))

class Something(object):
    pass

mapper(Something, table)    

# mimic application layers with some try blocks:
try:
    try:
        DBSession.begin_nested()
        DBSession.query(Something).all()
        DBSession.close()
        DBSession.query(Something).all()
    finally:
        # should direct conn.close() do rollback as 0.9.1 an earlier?
        conn.close()
finally:
    DBSession.close()
