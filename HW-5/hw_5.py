import aiohttp
import asyncio
import json
import platform
import sys

from datetime import datetime, timedelta


class HttpError(Exception):
    pass


async def request(url: str):
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


async def main(days: int, x=None):
    try:
        info = []
        for d in range(0, days + 1):
            delta = timedelta(days=d)
            date = datetime.now() - delta
            format_date = date.strftime("%d.%m.%Y")
            url = f"https://api.privatbank.ua/p24api/exchange_rates?date={format_date}"
            response = await request(url)
            currency = {"EUR", "USD", x}
            cur_dict = {}
            for i in response["exchangeRate"]:
                if i["currency"] in currency:
                    cur_dict[i["currency"]] = {"sale": i.get("saleRateNB"), "purchase": i.get("purchaseRateNB")}
            info.append({response["date"]: cur_dict})
        return info
    except HttpError as err:
        print(err)
        return None


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if len(sys.argv) > 1:
        index = int(sys.argv[1])
        if 0 <= index <= 10:
            if len(sys.argv) > 2:
                a = asyncio.run(main(days=index, x=sys.argv[2]))
            else:
                a = asyncio.run(main(days=index))
            print(json.dumps(a, indent=2))
        else:
            print(f"The entered value ({sys.argv[1]}) does not belong to the range from 0 to 10 inclusive.")
    else:
        print("Please enter the number of days as an argument.")
