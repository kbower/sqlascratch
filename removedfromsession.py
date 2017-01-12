# Show what happens when we use session.query().get()
# during a flush to load an object that is being inserted during the same flush
# Instead of getting what was the pending object, we get a new copy of what 
# the orm thinks is persistent and then it is detached after the flush finishes

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy import event
from sqlalchemy.orm.util import has_identity

engine = create_engine('sqlite:///', echo=True)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

rocks_table = Table("rocks", metadata,
    Column("id", Integer, primary_key=True),
)

bugs_table = Table("bugs", metadata,
    Column("id", Integer, primary_key=True),
    Column("rockid", Integer, ForeignKey('rocks.id'),),
)

class Rock(object):
    def __repr__(self):
        return '<Rock@%d: id=[%s] in session:[%s] has_identity[%s]>' % (id(self), self.__dict__.get('id'), self in session, has_identity(self))
    
class Bug(object):
    def __repr__(self):
        return '<Bug@%d: id=[%s] rockid[%s] with rock[%s]>' % (id(self), self.__dict__.get('id'), self.__dict__.get('rockid'), self.__dict__.get('rock','not set'))
    

class BugAgent(MapperExtension):
    def before_update(self, mapper, connection, instance):
        assert 'rock' not in instance.__dict__
        print "\n\n**** during flush"
        # after http://www.sqlalchemy.org/trac/ticket/2350, we could just reference like this:
        #instance.rock
        instance.rock = session.query(Rock).get(instance.rockid)
        #
        # we just loaded a Rock that was just inserted during this flush, so
        # it looks persistent to the orm, but the orm also has this object
        # already (still pending).  After the flush is done,
        # the pending object will be the only one in the session and the 
        # object we just loaded here will be removed from the session (detached)
        # 
        print "\n\n*****before_update: %r\n" % instance
        assert 'rock' in instance.__dict__
        

mapper(Rock, rocks_table,
    properties={'bugs': relationship(Bug,
                    cascade='all,delete-orphan', 
                    backref='rock')
                })    

mapper(Bug, bugs_table, extension=BugAgent())

@event.listens_for(Bug.rockid, 'set')
def autoexpire_rock_attribute(instance, value, oldvalue, initiator):
    if value != oldvalue:
        if instance in session and has_identity(instance):
            assert 'rock' in instance.__dict__
            print "\n\n****Bug.rockid changing from [%s] to [%s]..." % (oldvalue, value)
            print "******about to expire rock for %r" % instance
            session.expire(instance, ['rock'])
            print "******expired rock for %r\n" % instance
            assert 'rock' not in instance.__dict__


metadata.create_all()

session = Session()


# add a rock and bug
rock=Rock()
rock.id = 0
bug=Bug()
bug.id = 0
rock.bugs.append(bug)
session.add(rock)

session.commit()

# later... new session
session = Session()


b1 = Bug()
b1.id = 0

rock=Rock()
rock.id = 1
rock.bugs.append(b1)

print "\n\n****merge start\n"
merged = session.merge(rock)
print "\n\n****merge end\n"
print "****flush\n"
session.flush()

assert 'rock' in merged.bugs[0].__dict__

# show that the pending object has become persistent
print "\n\nsession's pending obj turned persistent:                         %r" % session.query(Rock).get(1)

# show that the object we loaded has been detached from the session
print 'merged.bugs[0].rock (copy of same object, no longer in session): %r' % merged.bugs[0].rock

