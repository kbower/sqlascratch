# I expected 4 queries total issued for the get() query below, but I get 11 instead.

from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///')
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

class Employee(object):
    pass

class Manager(Employee):
    pass

class Engineer(Employee):
    pass

class SupportTech(Employee):
    pass

class Role(object):
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

mapper(Role, roles_table)

employee_mapper = mapper(Employee, employees_table,
    polymorphic_on=employees_table.c.type,
    polymorphic_identity='E',
    properties = {
		'roles': relationship(Role),
        'staff': relationship(Employee,
            cascade='save-update,merge,refresh-expire,delete,delete-orphan', 
            single_parent=True,
            backref=backref('manager', remote_side=[employees_table.c.employee_id])),
        }
    )    
manager_mapper = mapper(Manager, inherits=employee_mapper,
                                    polymorphic_identity='M')
engineer_mapper = mapper(Engineer, inherits=employee_mapper,
                                    polymorphic_identity='E')
supporttech_mapper = mapper(SupportTech, inherits=employee_mapper,
                                    polymorphic_identity='S')

session = Session()

metadata.create_all()

try:
    m=Manager()
    m.employee_id = 1
    session.add(m)

    e=Engineer()
    e.employee_id = 2
    e.manager_id = 1
    session.add(e)

    s=SupportTech()
    s.employee_id = 3
    s.manager_id = 1
    session.add(s)

    session.flush()        
    session = Session()

    engine.echo = 'debug'
    e = session.query(Employee).options(
            subqueryload(Employee.staff),
            subqueryload(Employee.roles),
            subqueryload(Employee.staff,Employee.roles)
            ).get(1)

finally:
    engine.echo = False
    session.rollback()
    metadata.drop_all()


