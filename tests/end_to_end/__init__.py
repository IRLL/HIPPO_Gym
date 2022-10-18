import asyncio


async def server_client_interaction(server_coroutine, client_coroutine):
    server_task = asyncio.create_task(server_coroutine)
    client_task = asyncio.create_task(client_coroutine)
    _done, pending = await asyncio.wait(
        {server_task, client_task}, return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:  # Kill server when client is done
        task.cancel()
