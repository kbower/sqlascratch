from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('postgresql://salespylot:salespylot@localhost:5444/v12?application_name=Loft',echo=True)

metadata = MetaData(engine)
table=Table("sometable", metadata, 
    Column("id_a", Unicode(255), primary_key=True), 
    Column("id_b", Unicode(255)), 
)

i = Index('myfuncindex',
    func.coalesce(table.c.id_a, text("''")),
    func.coalesce(table.c.id_b, text("''")),
    unique=True
    )

metadata.create_all()

i.drop()

metadata.drop_all()
