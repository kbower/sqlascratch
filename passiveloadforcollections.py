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
                    if passive is attributes.PASSIVE_NO_FETCH:
                        #if prop.uselist:
                        #    return []
                        return attributes.PASSIVE_NO_RESULT
                    get_local_property_by_col = prop.parent.get_property_by_column
                    dict_ = state.obj().__dict__

                    qry = DBSession.query(prop.mapper)
                    # Caution: not part of public API, but sqla already knows
                    # if we should "use_get" instead of qry, so let's ask...
                    if prop._get_strategy(LazyLoader).use_get:
                        # Work out the pk of the related object we are to get()
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
       
class Order(Base, DeclareBase):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    
    lines = relationship("OrderLine")


class OrderLine(Base, DeclareBase):
    __tablename__ = 'orderline'
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    line_id = Column(Unicode, primary_key=True)


engine = create_engine('sqlite://', echo=False)

Order.metadata.create_all(engine)

DBSession = Session(engine)


engine.echo=True


ord = Order(id=1)

ord.lines = []