from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('oracle://arc:arc@localhost:1521/xe',echo=False)
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
session = Session()

import timeit
import __builtin__
__builtin__.__dict__.update(locals())

timer = timeit.Timer('metadata.reflect()','metadata.clear()')
print timer.repeat(repeat=4,number=1)





