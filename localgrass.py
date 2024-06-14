import asyncio
import random
import ssl
import json
import time
import uuid
import requests
import shutil
from loguru import logger
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent

user_agent = UserAgent()
random_user_agent = user_agent.random

async def connect_to_wss(socks5_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    logger.info(device_id)
    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": random_user_agent,
                "Origin": "chrome-extension://ilehaonighjijnmpnagapkhpcdbhclfg"
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            urilist = ["wss://proxy.wynd.network:4444/","wss://proxy.wynd.network:4650/"]
            uri = random.choice(urilist)
            server_hostname = "proxy.wynd.network"
            proxy = Proxy.from_url(socks5_proxy)
            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                     extra_headers=custom_headers) as websocket:
                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                        logger.debug(send_message)
                        await websocket.send(send_message)
                        await asyncio.sleep(20)

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(message)
                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "extension",
                                "version": "4.0.3"
                            }
                        }
                        logger.debug(auth_response)
                        await websocket.send(json.dumps(auth_response))

                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        logger.debug(pong_response)
                        await websocket.send(json.dumps(pong_response))
        except Exception as e:
            logger.error(e)
            logger.error(socks5_proxy)


async def main():
    #find user_id on the site in conlose localStorage.getItem('userId') (if you can't get it, write allow pasting)
    _user_id = input('2gCX1Rmhf2XDOIntNmaUIIkSaMb')
    with open('local_proxies.txt', 'r') as file:
            local_proxies = 'socks4://185.141.233.39:4153,45.128.133.209:1080,217.145.199.47:56746,92.42.8.21:4145,77.77.26.152:4153,31.179.162.78:4153,37.252.66.125:46324,95.43.244.15:4153,185.139.56.133:4145,156.67.115.5:4145,24.37.245.42:51056,185.82.218.171:1080,51.68.164.77:13938,178.32.202.54:47198,190.202.48.182:80,162.216.204.146:1080,46.34.144.199:4153,134.195.91.76:31991,201.184.239.75:5678,117.250.3.58:8080,124.41.213.174:5678,181.129.62.2:47377,79.106.170.126:4145,95.128.142.76:1080,190.14.5.166:5678,93.117.72.27:55770,176.97.190.118:3629,178.32.122.250:62074,212.50.19.150:4153,103.87.24.34:5678,185.89.181.212:5678,216.169.73.65:60221,190.232.8.125:5678,168.205.217.81:4145,51.161.33.206:16078,67.213.212.58:44041,51.68.164.77:19159,176.99.2.43:1080,31.7.65.18:443,103.253.153.242:41762,83.143.24.29:5678,37.18.73.60:5566,162.241.70.64:52744,178.32.202.54:3762,51.75.65.162:63918'
    tasks = [asyncio.ensure_future(connect_to_wss(i, _user_id)) for i in local_proxies ]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    #letsgo
    asyncio.run(main())
