from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('postgresql://salespylot:salespylot@localhost:5444/salespylot',echo=True)
metadata = MetaData()
Session = sessionmaker(bind=engine)
DBSession = Session()

mytable = Table("mytable", metadata,
    Column("id", Unicode, primary_key=True),
    Column("calculated", Unicode)
)


class Object(object):
    @property
    def calculated(self):
        return self._calculated
        
    @calculated.setter
    def calculated(self, calculated):
        self._calculated = calculated

mapper(Object, mytable,
    properties = {
        'calculated':synonym('_calculated', map_column=True)
})


