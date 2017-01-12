from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension, mark_changed
from zope.sqlalchemy import __version__ as zopesqlaversion
import transaction

print "zope.sqlalchemy version %s" % zopesqlaversion

engine = create_engine('sqlite:///', echo=True) 

session_maker = sessionmaker(bind=engine, extension=ZopeTransactionExtension())

Session = scoped_session(session_maker)
Session.execute("create table kb (data varchar)")
Session.execute("insert into kb values ('data')")
fetched = Session.execute("select * from kb").fetchall()
print "fetched: %r" % fetched
assert fetched == [('data',)]
# if we use sqla alone, Session.commit() would issue a commit
# zope.sqlalchemy thinks there is nothing to commit, unless there are changes to 
# actual sqla *objects* (then this would issue COMMIT)
mark_changed(Session())
transaction.commit()

Session = scoped_session(session_maker)
# now we see there was no data committed
fetched = Session.execute("select * from kb").fetchall()
print "fetched: %r" % fetched
assert fetched == [('data',)]

