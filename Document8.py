from sqlalchemy import *
from sqlalchemy.orm import *

#engine = create_engine('postgresql://un:pw@localhost:5444/salespylot',echo=True)
engine = create_engine('oracle://arc:arc@localhost:1521/xe?use_ansi=False',echo=True)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

engine.connect()
#engine.dialect.supports_native_decimal = False

orders_table = Table("orders", metadata,
    Column("orderid", Unicode(255), primary_key=True)
)


orderdetails_table = Table("orderdetails",metadata,
    Column("orderid", Unicode(255), ForeignKey('orders.orderid'), primary_key=True),
    Column("lineid", Integer, primary_key=True),
    Column("qtyordered", Numeric(20,2), nullable=False),
    Column("saleprice", Numeric(20,2), nullable=False),
)

class Order(object):
    pass

class OrderDetail(object):
    pass

order_mapper = mapper(Order, orders_table,
    properties={'orderdetails': relation(OrderDetail, 
                    cascade='all,delete-orphan', 
                    single_parent=True,
                    lazy=False,
                    backref=backref('parentorder',
                            cascade='refresh-expire,expunge'))
                })

od_alias=orderdetails_table.alias('od__a')
order_mapper.add_property('totalsale',
    # totalsale is an inline view column 
    column_property(cast(
        select([func.sum(od_alias.c.qtyordered * od_alias.c.saleprice)],
            orders_table.c.orderid==od_alias.c.orderid
        ).as_scalar(), Numeric(20,2)).label('totalsale')))


mapper(OrderDetail, orderdetails_table, allow_partial_pks=False)


print "\n\n%r\n\n" % session.query(Order).all()[0].totalsale

print "\n\n%r" %  session.query(Order).limit(100).all()[0].totalsale


