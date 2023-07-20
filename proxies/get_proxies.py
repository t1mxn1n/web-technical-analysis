import asyncio
import json

import aiohttp
from decouple import config

APIKEY = config('WEBSHARE_KEY')


async def get_proxies():
    url = 'https://proxy.webshare.io/api/proxy/list/'
    async with aiohttp.ClientSession(headers={"Authorization": APIKEY}) as session:
        async with session.get(url) as response:
            response_json = await response.json()
    proxy_list = response_json['results']
    proxy_strings = [
        f'http://{p["username"]}:{p["password"]}@{p["proxy_address"]}:{p["ports"]["http"]}'
        for p in proxy_list
        if p['valid']
    ]
    return proxy_strings


async def update_proxies():
    data = await get_proxies()
    json.dump(data, open('proxies.json', 'w'), indent=4)
    await asyncio.sleep(0.5)
