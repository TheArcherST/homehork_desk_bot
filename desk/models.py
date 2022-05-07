from sqlalchemy import create_engine, MetaData, Column, Integer, String, DateTime, Text, Time
from sqlalchemy.orm import declarative_base, sessionmaker


meta = MetaData()
sync_engine = create_engine("mysql+pymysql://root:2018Sport2018@localhost/hm_desk")
Base = declarative_base(sync_engine, metadata=meta)


Session = sessionmaker(sync_engine)


class Desk(Base):
    __tablename__ = 'desks'

    id = Column('id', Integer, primary_key=True, autoincrement=True)


class ScheduleItem(Base):
    __tablename__ = 'schedule_items'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    desk_id = Column('desk_id', Integer)

    objective = Column('objective', String(length=30))

    start = Column('start', DateTime)
    end = Column('end', DateTime)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    desk_id = Column('desk_id', Integer)
    lesson_id = Column('lesson_id', Integer)
    content = Column('content', Text)


meta.create_all()
