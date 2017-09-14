from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True) 
metadata = MetaData(engine)
session = sessionmaker(bind=engine)()

globalpreferences_table = Table("globalpreferences", metadata,
    Column("preferenceid", Unicode(255), primary_key=True),
    Column("value", Unicode(255))
)


sitepreferences_table = Table("sitepreferences", metadata,
    Column("preferenceid", Unicode(255), primary_key=True),
    Column("siteid", Unicode(255), primary_key=True),
    Column("value", Unicode(255))
)


userpreferences_table = Table("userpreferences", metadata,
    Column("preferenceid", Unicode(255), primary_key=True),
    Column("username", Unicode(255), primary_key=True),
    Column("value", Unicode(255))
)


def repr_attrs(obj, *attrs):
    """ 
    build a safe __repr__ string with obj.__dict__.get() so we don't
    accidentally set sqla attributes by referencing them
    """
    return '<%s: ' % obj.__class__.__name__ +  \
        ' '.join('{0[%s]}=[{1[%s]}]' % (i,i) for i in range(len(attrs)))\
            .format(attrs, map(obj.__dict__.get, attrs)) + ">"


class PreferenceBase(object):
    @classmethod
    def query(cls):
        """
        return a query
        """
        return session.query(cls)

    def __init__(self, prefid, val, **attrs):
        self.preferenceid = prefid
        self.value = val
        self.__dict__.update(attrs)

class GlobalPreference(PreferenceBase):

    def __repr__(self):
        return repr_attrs(self,'preferenceid','value')


class SitePreference(PreferenceBase):

    def __repr__(self):
        return repr_attrs(self,'preferenceid','siteid','value')

        
class UserPreference(PreferenceBase):

    def __repr__(self):
        return repr_attrs(self,'preferenceid','username','value')
    

preferences_union = polymorphic_union({
        'user': userpreferences_table,
        'site': sitepreferences_table,
        'global': globalpreferences_table
    }, 
    'type', 
    'preferences_union')

preferencebase_mapper = mapper(PreferenceBase, preferences_union,
    polymorphic_on=preferences_union.c.type
    )

mapper(GlobalPreference, globalpreferences_table,
    inherits=preferencebase_mapper,
    concrete=True,
    polymorphic_identity='global'
    )

mapper(SitePreference, sitepreferences_table,
    inherits=preferencebase_mapper,
    concrete=True,
    polymorphic_identity='site',
    )

mapper(UserPreference, userpreferences_table,
    inherits=preferencebase_mapper,
    concrete=True,
    polymorphic_identity='user',
    )


metadata.create_all(engine)

map(session.add, [
    GlobalPreference('prefA', 'gvalA'),
    GlobalPreference('prefB', 'gvalB'),
    GlobalPreference('prefC', 'gvalC'),
    SitePreference('prefB', 'svalB', siteid='00'),
    UserPreference('prefC', 'svalC', username='kb'),
    UserPreference('prefA', 'uvalA', username='kb'),
    UserPreference('prefB', 'uvalB', username='kb'),
    UserPreference('prefC', 'uvalC', username='jb'),
])

session.flush()
session.expunge_all()

u = polymorphic_union({
        'user': userpreferences_table.select().where(userpreferences_table.c.username=='kb'),
        'site': sitepreferences_table.select().where(sitepreferences_table.c.siteid=='00'),
        'global': globalpreferences_table
    }, 
    'type')

def apply_polymorphic_criteria(orig, target_table, criteria):
    from sqlalchemy.sql import visitors

    def provide_new_select(element):
        if target_table in element.froms:
            element.append_whereclause(criteria)

    return visitors.cloned_traverse(
        orig,
        {},
        {"select": provide_new_select}
    )

u = apply_polymorphic_criteria(
    preferences_union,
    userpreferences_table,
    userpreferences_table.c.username == 'kb'
)
u = apply_polymorphic_criteria(
    u,
    sitepreferences_table,
    sitepreferences_table.c.siteid == '00'
)

for i in PreferenceBase.query().with_polymorphic('*', selectable=u): print i


import pdb; pdb.set_trace()