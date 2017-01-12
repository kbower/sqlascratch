# coding: utf-8
from sqlalchemy import *
from sqlalchemy.orm import *

#engine = testing.db
engine = create_engine('oracle://arc:arc@localhost:1521/xe',echo=True)
metadata = MetaData(engine)

table=Table("atable", metadata, 
    Column("_underscorecolumn", Unicode(255), primary_key=True),
)
metadata.create_all()

try:
    table.insert().execute(
        {'_underscorecolumn': u'’é'},
    )
    result = engine.execute(
        table.select().where(table.c._underscorecolumn==u'’é')
    ).fetchall()
    assert result[0][0] == u'’é'
finally:
    metadata.drop_all()
