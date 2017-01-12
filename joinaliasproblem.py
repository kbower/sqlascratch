from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('postgresql://salespylot:salespylot@localhost:5444/salespylottest',echo=True)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()


orders_table = Table("orders", metadata,
    Column("orderid", Unicode(255), primary_key=True)
)


orderdetails_table = Table("orderdetails",metadata,
    Column("orderid", Unicode(255), ForeignKey('orders.orderid'), primary_key=True),
    Column("lineid", Integer, primary_key=True),
    Column("qtyordered", Numeric(20,2), nullable=False),
    Column("itemprice", Numeric(20,2), nullable=False),
    Column("voided", Unicode(1)),    
)

servicedetails_table = Table("servicedetails",metadata,
    Column("orderid", Unicode(255), primary_key=True),
    Column("lineid", Integer, primary_key=True),
    Column("sequence", Integer, primary_key=True),
    Column("qtyordered", Numeric(20,2), nullable=False),
    Column("itemprice", Numeric(20,2), nullable=False),
    Column("voided", Unicode(1)),    
    ForeignKeyConstraint(['orderid','lineid'],
        ['orderdetails.orderid', 'orderdetails.lineid'])
)

class Order(object):
    pass

class OrderDetail(object):
    pass

class ServiceDetail(object):
    pass

od_alias=orderdetails_table.alias('od__a')
sd_alias=servicedetails_table.alias('sd__a')

mapper(Order, orders_table,
    properties={
        'orderdetails': relation(OrderDetail, 
            cascade='all,delete-orphan', 
            single_parent=True,
            lazy=False),
        # totalsale is an inline view column 
        'totalsale': column_property(
                cast(
                    select([func.sum(sd_alias.c.qtyordered * sd_alias.c.itemprice)],
                        and_(orders_table.c.orderid==sd_alias.c.orderid, 
                            sd_alias.c.voided==text("'N'"),
                            od_alias.c.voided==text("'N'")),
                        from_obj=sd_alias.join(od_alias)).as_scalar(),
                Numeric(20,2)).label('totalsale'),
            deferred=False),
    })

mapper(OrderDetail, orderdetails_table)

mapper(ServiceDetail, servicedetails_table)


session.query(Order).all()
