import asyncio
import aiosqlite


async def get_db():
    return await aiosqlite.connect("img.db")

async def main():
    db = (await get_db())
    while True:
        query=input("Query: ")
        if query.lower()!="cancel":
            try:
                cursor=await db.execute(query)
            except Exception as exception:
                print(exception)
            else:
                try:
                    data = await cursor.fetchall()
                    for i in data:
                        print(i)
                except:
                    continue
                await db.commit()

if __name__=="__main__":
    asyncio.run(main())


