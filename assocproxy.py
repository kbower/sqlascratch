from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    kw = relationship("Keyword", secondary=lambda: userkeywords_table)

    def __init__(self, name):
        self.name = name
        
    # proxy the 'keyword' attribute from the 'kw' relationship
    keywords = association_proxy('kw', 'keyword')


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    keyword = Column('keyword', String(64))

    def __init__(self, keyword):
        self.keyword = keyword


userkeywords_table = Table('userkeywords', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"),
           primary_key=True),
    Column('keyword_id', Integer, ForeignKey("keyword.id"),
           primary_key=True)
)


engine = create_engine('sqlite:///', echo=True) 
Base.metadata.create_all(engine)

session = sessionmaker(bind=engine)()

session.query(User).filter(User.keywords.any()).all()