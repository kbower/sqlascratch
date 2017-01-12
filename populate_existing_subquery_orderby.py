# order by doesn't seem to always order correctly after populate_existing() refresh

from sqlalchemy import *
from sqlalchemy.orm import *
from operator import attrgetter

engine = create_engine('sqlite:///')
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

class Object(object):
    def __init__(self, **attrs):
        self.__dict__.update(attrs)

class Employee(Object):
    pass

class Manager(Employee):
    pass

class Engineer(Employee):
    pass

class Role(Object):
    pass

employees_table = Table('employees', metadata,
    Column('employee_id', Integer, primary_key=True),
    Column('type', String(1), nullable=False),
    Column('data', String(50)),
    Column('manager_id', Integer, ForeignKey('employees.employee_id')),
)

roles_table = Table('roles', metadata,
    Column('employee_id', Integer, ForeignKey('employees.employee_id'), primary_key=True),
    Column('role', String(50), primary_key=True),
)    

employee_mapper = mapper(Employee, employees_table,
    polymorphic_on=employees_table.c.type,
    polymorphic_identity='E',
    properties = {
        # NOTE: order_by
        'roles': relationship(Role, order_by=roles_table.c.role),
        'staff': relationship(Employee,
            cascade='save-update,merge,refresh-expire,delete,delete-orphan', 
            single_parent=True,
            backref=backref('manager', remote_side=[employees_table.c.employee_id])),
        }
    )    
mapper(Manager, inherits=employee_mapper,
    polymorphic_identity='M')
mapper(Engineer, inherits=employee_mapper,
    polymorphic_identity='E')

mapper(Role, roles_table)

session = Session()

metadata.create_all()

try:
    m=Manager(employee_id=1, data='manager')
    m.roles = [Role(role='role A'), Role(role='role F')]
    session.add(m)

    e=Engineer(employee_id=2, manager_id=1, data='engineer')
    e.roles = [Role(role='role K'), Role(role='role B')]
    session.add(e)

    engine.echo = 'debug'
    session.commit()        

    engine.echo = 'debug'
    e = session.query(Employee).options(
            subqueryload(Employee.staff),
            subqueryload(Employee.roles),
            subqueryload(Employee.staff,Employee.roles)
            ).get(1)

    sorter=attrgetter('role')
    assert e.roles==sorted(e.roles, key=sorter)
    assert e.staff[0].roles==sorted(e.staff[0].roles, key=sorter)

    # Now, we append 'role C' to the end of the collections.
    # After the populate_existing() refresh, we expect
    # the roles to be sorted according to the order_by, which
    # is the case for the Manager's, but not the Engineer's
    e.roles.append(Role(role='role C'))
    e.staff[0].roles.append(Role(role='role C'))
    
    print "Manager roles:\n" + "\n".join(r.role for r in e.roles)
    print "Engineer roles:\n" + "\n".join(r.role for r in e.staff[0].roles)

    session.flush()
    
    e = session.query(Employee)\
        .populate_existing()\
        .options(
                subqueryload(Employee.staff),
                subqueryload(Employee.roles),
                subqueryload(Employee.staff,Employee.roles)
            ).filter_by(employee_id=1).one()

    print "Updated Manager roles:\n" + "\n".join(r.role for r in e.roles)
    print "Updated Engineer roles:\n" + "\n".join(r.role for r in e.staff[0].roles)

    assert e.roles==sorted(e.roles, key=sorter)
    assert e.staff[0].roles==sorted(e.staff[0].roles, key=sorter)

finally:
    engine.echo = False
    session.rollback()
    metadata.drop_all()


