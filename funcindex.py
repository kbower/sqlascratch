from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy import __version__ as sqlaver

print("*** sqlalchemy: %s" % sqlaver)

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
    
i2 = Index('my2colindex',
    table.c.id_a,
    table.c.id_b)
    

metadata.create_all()

i.drop()
i2.drop()

i.create()
i2.create()

metadata.drop_all()
