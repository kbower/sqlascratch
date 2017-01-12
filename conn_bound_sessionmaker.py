from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exc import OperationalError
from sqlalchemy import event

eng = create_engine('postgresql://salespylot:salespylot@localhost:5444/sqla', 
    echo=True, pool_recycle=3600)
conn=eng.connect()
conn.info['locked_to_session'] = conn.connection.connection
# bind to specific connection
Session = scoped_session(sessionmaker(bind=conn))
_autonomous_maker = sessionmaker(bind=eng)

import pdb; pdb.set_trace()



class AutonomousSession(object):
    """with statement context manager for performing an autonomous transaction. See python's 'with' statement"""
    def __init__(self, explicit_modifies_database=False):
        self.session = _autonomous_maker()
        self.session.explicit_modifies_database = explicit_modifies_database
        
    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        # rollback to free resources. if they did a commit,
        # this won't do anything
        try:
            self.session.rollback()    
        finally:
            # sabotage this session so it is only used within 
            # context manager
            self.session.close()
            self.session.bind = None


def _connection_checkout(dbapi_connection, connection_record, connection_proxy):
    print repr(connection_record.info)
    print id(dbapi_connection)
    pass

def do_assert():
    return
    assert Session.connection().info.get('locked_to_session') is Session.connection().connection.connection , 'prevented problem'
    
event.listen(eng, 'checkout', _connection_checkout)

pid = conn.execute("select pg_backend_pid()").scalar()
raw_conn_addr = id(Session.connection().connection.connection)

metadata = MetaData(eng)
rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
)
class Rock(object):
    pass
mapper(Rock, rocks_table)
metadata.create_all()

do_assert()
Session.query(Rock).all()

# See if normally get same connection
Session.remove()
do_assert()
Session.query(Rock).all()

# all is good: we got original connection again:
assert pid == Session.connection().execute("select pg_backend_pid()").scalar()
assert raw_conn_addr == id(Session.connection().connection.connection)

# something drastic happens to conn
aux_conn=eng.connect()
aux_conn.execute(text("select pg_terminate_backend(:pid)"), 
    pid=pid)

try:
    do_assert()
    Session.query(Rock).all()
except OperationalError as e:
    print e
    # Error, framework automatically may issue this:
    Session.remove()

do_assert()
import pdb; pdb.set_trace()
Session.connection()
Session.query(Rock).all()

# New connection has been created, didn't anticipate this...
newpid = Session.connection().execute("select pg_backend_pid()").scalar()
new_addr = id(Session.connection().connection.connection)
print "%d != %d; %d != %d" % (pid, newpid, raw_conn_addr, new_addr)
assert pid == newpid or raw_conn_addr == new_addr

