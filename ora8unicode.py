#SHOW unicode problem with oracle 8 when inferring Column type

from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('oracle://user:pass@ip:1521/sid',echo=True)
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

orders_table = Table("orders", metadata,
    Column("orderid", Unicode(255), primary_key=True),
    Column("shipzipcode", ForeignKey('zipcodes.zipcode'))
)


zipzones_table = Table("zipzones", metadata,
    Column("zoneid", ForeignKey('zones.zoneid'), primary_key=True),
    Column("zipcode", Unicode(255))
)

zones_table = Table("zones", metadata,
    Column("zoneid", Unicode(255), primary_key=True)
)

zipcodes_table = Table('zipcodes', metadata,
    Column("zipcode", Unicode(9), primary_key=True)
)

class Order(object):
    pass

class Zone(object):
    pass    

mapper(Zone, zones_table)

mapper(Order, orders_table, 
    properties={'defaultzones': relationship(Zone,
        secondary=zipzones_table,
        primaryjoin=orders_table.c.shipzipcode==zipzones_table.c.zipcode,
        foreign_keys=[zipzones_table.c.zipcode, zones_table.c.zoneid],
        order_by=zones_table.c.zoneid)}
)

ord=DBSession.query(Order).filter_by(orderid=u'0109009OICY').one()


ord.defaultzones



