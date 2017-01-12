from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('oracle://arc:arc@localhost:1521/xe',echo=True)
engine.connect()
print "*****************************"
print "server_version_info: ", engine.dialect.server_version_info
print "_supports_char_length: ", engine.dialect._supports_char_length
print "supports_unicode_binds: ", engine.dialect.supports_unicode_binds
print "use_ansi:", engine.dialect.use_ansi
print "*****************************"

metadata = MetaData()
Session = sessionmaker(bind=engine)
DBSession = Session()

table = Table("tabl", metadata,
    Column("col", String(255), primary_key=True)
)

class Record(object):
    pass

mapper(Record, table)

r=Record()
r.col = u'Unicode String'


metadata.create_all(engine)
DBSession.add(r)
DBSession.flush()


