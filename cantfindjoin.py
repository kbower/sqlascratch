from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm import configure_mappers

engine = create_engine('sqlite:///', echo=True)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)

mod_valueplans_table = Table("mod_valueplans", metadata,
    Column("productid", Unicode(255), primary_key=True),
    Column("planid", Integer, autoincrement=False, primary_key=True)
)

mod_valueplanprices_table = Table('mod_valueplanprices', metadata,
    Column("productid", Unicode(255), primary_key=True),
    Column("planid", Integer, autoincrement=False, primary_key=True),
    Column("ceiling", Numeric(20,2), primary_key=True),
    ForeignKeyConstraint(['productid','planid'],
        ['mod_valueplans.productid','mod_valueplans.planid']),
)

class MorValuePlan(object):
    pass

class MorValuePlanPrice(object):
    pass

mapper(MorValuePlan, mod_valueplans_table,
    properties={
        'prices': relationship(MorValuePlanPrice,
            order_by=mod_valueplanprices_table.c.ceiling,
            single_parent=True,)
    })

mapper(MorValuePlanPrice, mod_valueplanprices_table)

configure_mappers()

metadata.create_all()
try:
    pass
finally:
    metadata.drop_all()
    
