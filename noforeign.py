from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('sqlite:///', echo=True) 
metadata = MetaData(engine)
session = sessionmaker(bind=engine)()

# association table
post_keywords = Table('post_keywords', metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('keyword_id', Integer, ForeignKey('keywords.id'))
)

posts_table = Table('posts', metadata,
    Column('id', Integer, primary_key=True),
    Column('headline', String(255), nullable=False),
    Column('body', Text)
)

keywords_table = Table('keywords', metadata,
    Column('id', Integer, primary_key=True),
    Column('keyword', String(50), nullable=False, unique=True)
)

spotlights_table = Table('spotlights', metadata,
    Column('id', Integer, primary_key=True),
    Column('enddate', Date),
    Column('post_id', Integer, ForeignKey('posts.id'))
)
    
class BlogPost(object):
    def __init__(self, headline, body):
        self.headline = headline
        self.body = body

    def __repr__(self):
        return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)

class Keyword(object):
    def __init__(self, keyword):
        self.keyword = keyword

class PostSpotLight(object):
    pass

mapper(Keyword, keywords_table)

mapper(BlogPost, posts_table,
    properties = {'keywords':
        relationship(Keyword, secondary=post_keywords, backref='posts')}
)

mapper(PostSpotLight, spotlights_table,
    properties = {'postkeywords':
        relationship(Keyword, secondary=post_keywords,
            primaryjoin=spotlights_table.c.post_id==post_keywords.c.post_id,
#            foreign_keys=[post_keywords.c.post_id,post_keywords.c.keyword_id],
            )}
)
    
metadata.create_all(engine)
compile_mappers()

