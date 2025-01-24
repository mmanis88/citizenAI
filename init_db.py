import asyncio

from database import init_db


async def main():
    await init_db()


asyncio.run(main())
