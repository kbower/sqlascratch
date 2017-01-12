# confirms that 'delete' in cascade (or 'all') actually deletes the related object, not just the linking record in M:N

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

class BlogPost(object):
    def __init__(self, headline, body):
        self.headline = headline
        self.body = body

    def __repr__(self):
        return "BlogPost(%r, %r, %r)" % (self.headline, self.body, self.author)

class Keyword(object):
    def __init__(self, keyword):
        self.keyword = keyword

mapper(Keyword, keywords_table)

mapper(BlogPost, posts_table,
    properties = {'keywords':
        relationship(Keyword, secondary=post_keywords, cascade='all', backref='posts')}
)

metadata.create_all(engine)

keywords = [
    Keyword('church'),
    Keyword('temple'),
    Keyword('dayout'),
    Keyword('special'),
]
blogs = [
    BlogPost('Youth Trip','Went to temple.'),
    BlogPost('Family day','Spent at Nauvoo.'),
]

map(session.add, keywords)
map(session.add, blogs)

blogs[0].keywords = keywords[:2]
blogs[1].keywords = keywords[1:]

session.flush()

session.expunge_all()

import pdb; pdb.set_trace()

b=session.query(BlogPost).filter(BlogPost.headline=='Youth Trip').one()
session.delete(b)


session.flush()

