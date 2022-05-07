from sqlalchemy import create_engine, MetaData, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker


meta = MetaData()
sync_engine = create_engine('sqlite:///data.db')
Base = declarative_base(sync_engine, metadata=meta)


Session = sessionmaker(sync_engine)


class User(Base):
    __tablename__ = 'users'

    user_id = Column('user_id', Integer, primary_key=True)

    username = Column('username', String)
    last_activity = Column('last_activity', DateTime)


meta.create_all()
