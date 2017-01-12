from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite://') 
Session = sessionmaker(bind=engine)
session = Session()

session.execute("create table ab (data varchar)")
engine.echo = True
session.execute("create table bc (data varchar)")
