import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
import names
import websockets
from aiofile import AIOFile, Writer
from aiopath import AsyncPath
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK


logging.basicConfig(level=logging.INFO)


class HttpError(Exception):
    pass


async def log_to_file(mes: str, filepath: str = "log.txt"):
    log_file = AsyncPath(filepath)
    if not await log_file.exists():
        await log_file.touch()

    async with AIOFile(log_file, "a", encoding="utf-8") as afp:
        writer = Writer(afp)
        await writer(f"{datetime.now()}: {mes}\n")


async def request(url: str) -> dict | str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
            raise HttpError(f"Connection error: {url}", str(err))


async def get_exchange(index: int = 0):
    try:
        info = []
        for d in range(0, index + 1):
            delta = timedelta(days=d)
            date = datetime.now() - delta
            format_date = date.strftime("%d.%m.%Y")
            url = f"https://api.privatbank.ua/p24api/exchange_rates?date={format_date}"
            response = await request(url)
            currency = {"EUR", "USD"}
            cur_dict = {}
            for i in response["exchangeRate"]:
                if i["currency"] in currency:
                    cur_dict[i["currency"]] = {"sale": i.get("saleRateNB"), "purchase": i.get("purchaseRateNB")}
            info.append({response["date"]: cur_dict})
        return str(info)
    except HttpError as err:
        print(err)
        return None


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            parts = message.split()
            if parts[0] == "exchange":
                await log_to_file(message)
                if len(parts) == 1:
                    exchange = await get_exchange()
                elif len(parts) == 2:
                    exchange = await get_exchange(int(parts[1]))
                await self.send_to_clients(exchange)
            elif message == "Hello server":
                await self.send_to_clients("Привіт мої карапузи")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
