import asyncio
from db import engine, Base, AsyncSessionLocal
from models import User
from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def create_user(name, care_name, phone, raw_password):
    async with AsyncSessionLocal() as session:
        try:
            hashed_password = bcrypt.hash(raw_password)
            user = User(name=name, care_name=care_name, phone=phone, password=hashed_password)
            session.add(user)
            await session.commit()
            print("✅ Пользователь добавлен")
        except IntegrityError:
            await session.rollback()
            print("❌ Такой пользователь уже существует")
        except Exception as e:
            await session.rollback()
            print(f"❌ Другая ошибка: {e}")
        finally:
            await session.close()

async def main():
    await create_tables()
    await create_user("Айша", "Адам", "89991234567", "mypassword")

if __name__ == "__main__":
    asyncio.run(main())
