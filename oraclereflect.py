from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('oracle://kent:kent@localhost:1521/xe',echo=False)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
session = Session()

order_table = Table("orders", metadata,
    Column("id_a", Unicode(255), primary_key=True),
    Column("id_b", Unicode(255), primary_key=True)
)


metadata.create_all()

metadata.clear()

metadata.reflect()

for con in metadata.tables['orders'].constraints:
    print "type: %s" % con
    print "name: %s"% con.name
    print "columns: %r" % [c.name for c in con.columns]


res = engine.execute("""
SELECT  ac.constraint_name,
     ac.constraint_type,
     loc.column_name AS local_column,
     rem.table_name AS remote_table,
     rem.column_name AS remote_column,
     rem.owner AS remote_owner,
     loc.position as loc_pos,
     rem.position as rem_pos
   FROM all_constraints ac,
     all_cons_columns loc,
     all_cons_columns rem
   WHERE ac.table_name = 'ORDERS'
   AND ac.constraint_type IN ('R','P')
   AND ac.owner = 'KENT'
   AND ac.owner = loc.owner
   AND ac.constraint_name = loc.constraint_name
   AND ac.r_owner = rem.owner(+)
   AND ac.r_constraint_name = rem.constraint_name(+)
   AND (rem.position IS NULL or loc.position=rem.position)
   ORDER BY ac.constraint_name, loc.position
""").fetchall()

print "\n".join([r.__repr__() for r in res])

