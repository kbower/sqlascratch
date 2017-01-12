#!/usr/bin/python
# test sqlalchemy memory leak introduced in 0.7.5
# please refer to http://www.sqlalchemy.org/trac/ticket/2427
# Author: Iuri Diniz
import gc

from sqlalchemy import create_engine, Table, __version__
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, String
from sqlalchemy.orm import sessionmaker

#url = 'sqlite:///:memory:'
#url = 'mysql://test:1234@localhost/test_%s?charset=utf8' %(
# __version__.replace(".", "_"),)
#url = 'mysql://test:1234@localhost/test?charset=utf8'
url = 'postgresql://salespylot:salespylot@localhost:5444/salespylot'

engine = create_engine(url)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True)
    key = Column(Unicode(80), unique=True)
    value = Column(Unicode(256))

    def __repr__(self):
        return "%s.%s(id=%r, key=%r, value=%r)" % (
            self.__class__.__module__,
           self.__class__.__name__,
           self.id, self.key,
           self.value)

log_table = Table('log_table', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('int1', Integer, nullable=False),
    Column('str1', String(20)),
    Column('str2', String(50)),
    Column('str3', String(50)),
    Column('str4', String(50)),
    Column('str5', String(50)),
    Column('str6', String(50)),
    Column('str7', String(50)),
    Column('str8', String(50)),
)


class LogTable(Base):
    __table__ = log_table

    def __repr__(self):
        return (("%s.%s(id=%r, int1=%r, str1=%r, " +
                 "str2=%r, str3=%r, str4=%r, str5=%r, " +
                 "str6=%r, str7=%r, str8=%r)") %
                (self.__class__.__module__, self.__class__.__name__,
                 self.id, self.int1,
                 self.str1, self.str2, self.str3,
                 self.str4, self.str5, self.str6,
                 self.str7, self.str8))


def log_gen(session):
    while True:
        yield True
        # generate some entries
        for i in range(0,10):
            log_entry = LogTable(int1=10-i,
                                 str1="blaw", str2="blew", str3="bliw",
                                 str4="blow", str5="bluw", str6="ahua",
                                 str7="nil", str8="nul")
            session.add(log_entry)

        session.flush()


def process_gen(session):
    while True:
        yield True
        last_id = session.query(Config).filter(Config.key==u"last_id").one()
        filter_by_id = "id > %d" %(int(last_id.value))
        query_set = session.query(LogTable)
        query_set = query_set.filter(filter_by_id)
        query_set = query_set.order_by(LogTable.id)
        query_set.count()

        for log_entry in query_set:
            # process log
            
            #print "PROCESSING: %r" % (log_entry,)

            # save last processed log
            last_id.value = unicode(log_entry.id)
        
        #print "Last ID: %r" %(last_id)
        session.flush()


if __name__ == "__main__":
    session = Session()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    last_id = Config(key=u"last_id", value=u"1")
    session.add(last_id)
    session.flush()

    interation1 = log_gen(session)
    interation2 = process_gen(session)
    
    counts = [0 for i in range(0,10)]

    for i in range(0,10):
        interation1.next() and interation2.next()
        # force garbage collector
        gc.collect()
        gc_count = len(gc.get_objects())
        counts[i] = gc_count

    leak = all([counts[i] > counts[i-1] for i in range(1,10)])

    print "sqlalchemy.__version__ = %s, leak = %r" %(__version__, leak)
