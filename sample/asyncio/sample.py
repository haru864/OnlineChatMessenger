import asyncio
import time

num = 0


async def async_task(duration):
    print(f"Task started - will take {duration} seconds.")
    await asyncio.sleep(duration)
    # time.sleep(duration)
    print(f"Task finished after {duration} seconds.")
    global num
    num += 1


async def async_task_02(start, end):
    for n in range(start, end + 1):
        print(n)


async def main():
    print(f"started at {time.strftime('%X')}")
    # task1 = asyncio.create_task(async_task(2))
    # task2 = asyncio.create_task(async_task(5))
    # await task1
    # await task2
    task1 = asyncio.create_task(async_task_02(1, 9))
    task2 = asyncio.create_task(async_task_02(10, 19))
    await task1
    await task2
    print(f"finished at {time.strftime('%X')}")
    global num
    print(num)


asyncio.run(main())
