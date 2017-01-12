from sqlalchemy import *
from sqlalchemy.orm import *

eng_url = 'oracle://kent:kent@localhost:1521/xe?use_ansi=False'

engine = create_engine(eng_url, echo=True)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)


products_table = Table("products", metadata,
    Column("productid", Unicode(255), primary_key=True),
)


inventory_table = Table("inventory", metadata,
    Column("inventoryid", Integer, primary_key=True),

    Column("productid", Unicode(255), ForeignKey('products.productid'), nullable=False),

    Column("siteid", Unicode(255), nullable=False),

    Column("qty", Integer, nullable=False),
)


def repr_attrs(obj, *attrs):
    return '<%s: ' % obj.__class__.__name__ +  \
        ' '.join('{0[%s]}=[{1[%s]}]' % (i,i) for i in range(len(attrs)))\
            .format(attrs, map(obj.__dict__.get, attrs)) + ">"
            
            
class Base(object):
    def __init__(self, session, **attrs):
        self.__dict__.update(attrs)
        session.add(self)


class SiteStockLevel(object):
    def __repr__(self):
        return repr_attrs(self,'productid','siteid','qty')


class Product(Base):
    def __repr__(self):
        return repr_attrs(self,'productid')


class Inventory(Base):
    pass


sitestocklevels_view = select([
        inventory_table.c.productid, 
        inventory_table.c.siteid, 
        func.sum(inventory_table.c.qty).label('qty')],
    group_by=[inventory_table.c.productid, inventory_table.c.siteid]).alias('sitestocklevels')


mapper(Inventory, inventory_table)


mapper(Product, products_table, 
    properties={
            'sitestocklevels': relationship(SiteStockLevel,
                primaryjoin=sitestocklevels_view.c.productid==products_table.c.productid,
                order_by=sitestocklevels_view.c.siteid,
                viewonly=True),
    })
    

mapper(SiteStockLevel, sitestocklevels_view, 
    primary_key=[sitestocklevels_view.c.productid, sitestocklevels_view.c.siteid])
        

metadata.create_all()
try:
    sess = Session()
    Product(sess, productid=u'SKUA')
    Product(sess, productid=u'SKUB')
    sess.commit()
    Inventory(sess, inventoryid=1, productid=u'SKUA', siteid=u'S1', qty=1)
    Inventory(sess, inventoryid=2, productid=u'SKUA', siteid=u'S1', qty=2)
    Inventory(sess, inventoryid=3, productid=u'SKUA', siteid=u'S1', qty=3)
    Inventory(sess, inventoryid=4, productid=u'SKUA', siteid=u'S2', qty=1)
    sess.commit()
    
    allproducts = sess.query(Product).options(joinedload(Product.sitestocklevels)).all()
    
    assert len(allproducts) == 2
     
finally:
    metadata.drop_all()
    
