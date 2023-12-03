from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('postgresql+psycopg2://postgres:postgres@db/postgres')

def init():
    Base.metadata.create_all(engine)


class DBKey(Base):
    __tablename__ = 'keys'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(String)


class DBPix(Base):
    __tablename__ = 'pix'
    id = Column(Integer, primary_key=True)
    key = Column(String)
    amount = Column(Integer)


def db_create_key(key: dict):
    Session = sessionmaker(bind=engine)
    session = Session()
    db_key = DBKey(name=key.get('key'), owner=key.get('owner'))
    session.add(db_key)
    session.commit()
    session.close()

def db_get_key(owner: str):
    print(f"buscando chave: {owner}")
    Session = sessionmaker(bind=engine)
    session = Session()
    item = session.query(DBKey).filter(DBKey.owner==owner.lower()).first()
    print(item)
    session.close()

    if item is None:
        return None
    
    key = {"name": item.name, "owner": item.owner}
    return key

def db_pix_key(data: dict):
    Session = sessionmaker(bind=engine)
    session = Session()
    db_key = DBPix(key=data.get('key'), amount=data.get('amount'))
    session.add(db_key)
    session.commit()
    session.close()