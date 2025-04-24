from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session
from database.db import engine  # подключение к БД

def create_record(table, data: dict):
    with Session(engine) as session:
        session.execute(insert(table).values(**data))
        session.commit()
        print("✔ Создана запись:", data)

def read_all(table):
    with Session(engine) as session:
        result = session.execute(select(table)).fetchall()
        for row in result:
            print(dict(row._mapping))
        return result

def update_record(table, record_id: int, data: dict):
    with Session(engine) as session:
        stmt = update(table).where(table.c.id == record_id).values(**data)
        session.execute(stmt)
        session.commit()
        print(f"✔ Обновлена запись ID {record_id}:", data)

def delete_record(table, record_id: int):
    with Session(engine) as session:
        stmt = delete(table).where(table.c.id == record_id)
        session.execute(stmt)
        session.commit()
        print(f"✔ Удалена запись ID {record_id}")
