from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.properties import RelationshipProperty, MANYTOONE
import pickle
from sqlalchemy.orm.util import has_identity, with_parent
from sqlalchemy.ext import serializer
from sqlalchemy.orm.attributes import instance_state, ATTR_WAS_SET

Base = declarative_base()

def many_to_one_props(mapper):
    for prop in mapper.iterate_properties:
        if isinstance(prop, RelationshipProperty) and \
                prop.direction == MANYTOONE:
            yield prop

def deferred_transient_callable(prop, crit, state, dict_):
    def go(**kw):
        result = session.query(prop.mapper).filter(crit).one()
        
        # pop out the callable...
        state.reset(dict_, prop.key)
        
        # populate the result via dict.  this produces no
        # net change during flush, relying upon the FK 
        dict_[prop.key] = result
        
        # or, populate the result with a "change" event.
        # the UOW picks it up during flush.
        # state.get_impl(prop.key).set(state, dict_, result, None)
        
        # tell the InstrumentedAttribute "its handled"
        return ATTR_WAS_SET
    return go
    
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    related_id = Column(Integer, ForeignKey('related.id'))
    some_other_id = Column(Integer, ForeignKey('some_other.id'))
    
    related = relationship("Related")
    some_other = relationship("SomeOther")
    
    def __getstate__(self):
        if not has_identity(self):
            d = self.__dict__.copy()
            
            mapper = object_mapper(self)
            for prop in many_to_one_props(mapper):
                for l, r in prop.local_remote_pairs:
                    if mapper.get_property_by_column(l).key not in d:
                        break
                else:
                    d[prop.key] = serializer.dumps(with_parent(self, prop))
            return d
        else:
            return self.__dict__
            
    def __setstate__(self, d):
        self.__dict__.update(d)
        if not has_identity(self):
            state = instance_state(self)
            for prop in many_to_one_props(object_mapper(self)):
                if prop.key in self.__dict__:
                    crit = serializer.loads(
                        self.__dict__[prop.key],
                        metadata = self.metadata,
                    )
                    state.set_callable(self.__dict__, prop.key, deferred_transient_callable(
                        prop, crit, state, self.__dict__
                    ))
        
class Related(Base):
    __tablename__ = 'related'
    id = Column(Integer, primary_key=True)

class SomeOther(Base):
    __tablename__ = 'some_other'
    id = Column(Integer, primary_key=True)


engine = create_engine('postgresql://salespylot:salespylot@localhost:5444/salespylottest', echo='debug')

Base.metadata.create_all(engine)

session = Session(engine)

rel = Related()
session.add(rel)
session.commit()

p1 = Parent(related_id=rel.id)
dump = pickle.dumps(p1)
load= pickle.loads(dump)

# not present
assert 'related' not in load.__dict__

# load
print load.related

# present !
assert 'related' in load.__dict__

assert load.related is rel

session.add(load)
session.commit()

print load.related
assert load.related is rel

dump = pickle.dumps(load)
load2 = pickle.loads(dump)

print load2.related
assert load2.related is not rel # since it was serialized normally

load2 = session.merge(load2)
assert load2.related is rel
