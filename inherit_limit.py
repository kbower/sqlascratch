from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

class Employee(object):
    pass

class Manager(Employee):
    pass

class Engineer(Employee):
    pass

class Role(object):
    pass

employees_table = Table('employees', metadata,
    Column('employee_id', Integer, primary_key=True),
    Column('type', String(20), nullable=False)
)

roles_table = Table('roles', metadata,
    Column('employee_id', Integer, ForeignKey('employees.employee_id'), primary_key=True),
    Column('role', String(50), primary_key=True),
)    

mapper(Role, roles_table)

employee_mapper = mapper(Employee, employees_table,
    polymorphic_on=case(value=employees_table.c.type, whens={
        'E': 'employee',
        'M': 'manager'
        }),
    polymorphic_identity='employee',
    properties = {
        'roles': relationship(Role),
        }
    )
manager_mapper = mapper(Manager, inherits=employee_mapper,
                                    polymorphic_identity='manager')
engineer_mapper = mapper(Engineer, inherits=employee_mapper,
                                    polymorphic_identity='engineer')

session = Session()

metadata.create_all()

try:
    m=Manager()
    m.type = 'M'
    m.employee_id = 1
    session.add(m)

    q = session.query(Employee).options(joinedload('roles')).limit(10).all()
finally:
    session.rollback()
    metadata.drop_all()


