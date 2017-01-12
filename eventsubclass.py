from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy import event

engine = create_engine('sqlite:///', echo=0)
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


@event.listens_for(Employee, 'before_insert', propagate=True)
def before_emp_insert(mapper, connection, instance):
    print "\n\n***before Employee insert\n\n"


@event.listens_for(Employee.roles, 'append', propagate=True)
def rel_append(instance, value, initiator):
    print "\n\nappending %r\n\n" % value



session = Session()
metadata.create_all()

try:
    m=Manager()
    m.type = 'M'
    m.employee_id = 1
    session.add(m)
    
    r=Role()
    r.role = 'keyholder'
    m.roles = [r]
    
    session.flush()
    
finally:
    session.rollback()
    metadata.drop_all()


