import asyncio
from db import AsyncSessionLocal
from models import User
from sqlalchemy import select
from passlib.hash import bcrypt

async def check_credentials(phone, password):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.phone == phone))
        user = result.scalar_one_or_none()
        if user and bcrypt.verify(password, user.password):
            print("✅ Вход выполнен")
            return user
        else:
            print("❌ Неверный номер или пароль")
            return None

if __name__ == "__main__":
    asyncio.run(check_credentials("89991234567", "mypassword"))
