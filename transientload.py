"""
If your project uses serialization techniques with sqlalchemy, you may
find the need to load persistent relations from transient or pending objects.  

For example, you may have deserialized an object in order to perform calculations with it.
You may have no intention to add it to the database at this point (transient) 
or you may be working in a controlled environment with session.autoflush == False (pending)
while you do validations or other calculations before the session.flush()
"""
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.strategies import LazyLoader
from sqlalchemy.orm import attributes
import logging

log = logging.getLogger(__name__)

class InstallCustomizedAttribute(InstrumentationManager):
    def post_configure_attribute(self, class_, attr, inst):
        """
        Set up function to be invoked when relations are 'get'ed on possibly
        transient objects, so we can manually query these related objects
        """
        if isinstance(inst.property, RelationshipProperty):
            default_loader = inst.impl.callable_
            def create_getattr_when_never_set(state):
                if state.has_identity:
                    # this is a persistent (or detached) object, so instead 
                    # of a custom function, return default sqla functionality
                    return default_loader(state)
                def getattr_when_never_set(passive):
                    prop = inst.property
                    get_local_property_by_col = prop.parent.get_property_by_column
                    dict_ = state.obj().__dict__

                    qry = DBSession.query(prop.mapper)
                    # Caution: not part of public API, but sqla already knows
                    # if we should "use_get" instead of qry, so let's ask...
                    if prop._get_strategy(LazyLoader).use_get:
                        # Work out the fk
                        rem_pk_ident = []
                        local_fk_from_remote = dict([(r, l) for l, r in prop.local_remote_pairs])
                        # Loop over the ordered primary key of related property
                        for remote_pk in prop.mapper.primary_key:
                            val = dict_.get(get_local_property_by_col(local_fk_from_remote[remote_pk]).key, None)
                            if val is None:
                                # fk not fully set, so no lookup
                                # (Note: if you allow_partial_pks, need extra logic here)
                                return None
                            rem_pk_ident.append(val)
                        result = qry.get(rem_pk_ident)
                    else:
                        table = prop.parent.mapped_table
                        for l, r in prop.local_remote_pairs:
                            if l.table == table and \
                               dict_.get(get_local_property_by_col(l).key, None) is None:                            
                                # fk not fully set, so no lookup
                                # (Note: if you allow_partial_pks, need extra logic here)
                                return None                        
                        result = qry.with_parent(state.obj(), attr).all()
                        if not prop.uselist:
                            l = len(result)
                            if l:
                                if l > 1:
                                    log.error(
                                        "Multiple rows returned with "
                                        "uselist=False for attribute '%s' "
                                        % prop)
                                result = result[0]
                            else:
                                result = None

                    # populate the result via dict.  this produces no
                    # net change during flush, relying upon the FK 
                    dict_[attr] = result

                    # tell the InstrumentedAttribute "its been set"
                    return attributes.ATTR_WAS_SET
                return getattr_when_never_set
            inst.impl.callable_ = create_getattr_when_never_set

DeclareBase = declarative_base()

class Base(object):
# comment out the next line to compare the "normal" behavior
    __sa_instrumentation_manager__ = InstallCustomizedAttribute
    pass
    
class Shipping(Base, DeclareBase):
    __tablename__ = 'shipping'
    id = Column(Integer, primary_key=True)
    type = Column(Unicode)
    def __repr__(self):
        return '<Shipping: %s "%s">' % (self.id, self.type)

class Promotion(Base, DeclareBase):
    __tablename__ = 'promotion'
    id = Column(Unicode, primary_key=True)
    discount = Column(Numeric)
    def __repr__(self):
        return '<Promotion: %s discount: %s>' % (self.id, self.discount)
    
class ShippingZip(Base, DeclareBase):
    __tablename__ = 'shipzip'
    ship_id = Column(Integer, ForeignKey('shipping.id'), primary_key=True)
    zip_code = Column(Integer, primary_key=True)    
    
class Order(Base, DeclareBase):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    promotion_id = Column(Unicode, ForeignKey('promotion.id'))
    zip_code = Column(Integer)

    promotion = relationship("Promotion")
    shippingchoices = relationship("Shipping",
                    secondary=ShippingZip.__table__,
                    primaryjoin= zip_code==ShippingZip.zip_code,
                    foreign_keys=[ShippingZip.zip_code, Shipping.id])
    def __repr__(self):
        return '<Order: %s>' % self.id


engine = create_engine('sqlite://', echo=False)

Order.metadata.create_all(engine)

DBSession = Session(engine)

# add static, persistent data
data = (Shipping(type=u'Next Day', id=1),
ShippingZip(zip_code=29332, ship_id=1),
ShippingZip(zip_code=29000, ship_id=1),
Shipping(type=u'Ground', id=2),
ShippingZip(zip_code=29332, ship_id=2),
ShippingZip(zip_code=35444, ship_id=2),
Shipping(type=u'Slow', id=3),
ShippingZip(zip_code=88005, ship_id=3),
ShippingZip(zip_code=35444, ship_id=3),
Promotion(id=u'COUPON_A', discount=5),
Promotion(id=u'PROMO_B', discount=25),
Promotion(id=u'PROMO_C', discount=35),
)

for obj in data:
    DBSession.merge(obj)

DBSession.commit()

DBSession.expunge_all()

# Demo

engine.echo=True

# Your deserialization routines create an order with some fk
# data populated

ord=Order()
ord.zip_code = 29332
ord.promotion_id = u'PROMO_B'

# Now you can reference the persistent data on the transient object as needed,
# so long as the fks have been set:

print "\n(Transient) ord.promotion = %r\n" % ord.promotion 
print "\n(Transient) ord.shippingchoices = %r" % ord.shippingchoices

# If a many to one is in the session, we don't need a trip to the database:

another_ord = Order(zip_code=88005, promotion_id=u'PROMO_B')

DBSession.autoflush=False
DBSession.add(another_ord)

print "\n(Pending) another_ord.promotion = %r" % another_ord.promotion 
