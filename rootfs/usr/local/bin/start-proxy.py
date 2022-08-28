#!/usr/bin/env python

import os
import sys
import time
import logging
import getopt
import contextlib
import aiohttp
import asyncio
from sanic import Sanic
from urllib.request import urlopen
from multiprocessing import Manager
from asyncio.exceptions import CancelledError
from aiohttp.client import ClientRequest
from aiohttp.client_exceptions import ClientConnectorError


app = Sanic(__name__)
logger = logging.getLogger(__name__)

RELAY_PATHS = ["api/v2/write", "api/v2/delete"]

RELAY_BACKENDS = Manager().dict()
for index, url in enumerate(os.environ.get('RELAY_BACKENDS', 'http://localhost').split(",")):
    RELAY_BACKENDS[url] = (int(time.time()), index * 10)
RELAY_BACKENDS_INTERVAL = int(os.environ.get("RELAY_BACKENDS_INTERVAL", 3600 * 24 * 2))
RELAY_BACKENDS_BLOCK_TIME = int(os.environ.get("RELAY_BACKENDS_BLOCK_TIME", 60 * 1))
RELAY_BACKENDS_BLOCK_LIST = Manager().list()


async def check_health_task(app):
    await asyncio.sleep(RELAY_BACKENDS_BLOCK_TIME)
    while True:
        for url in RELAY_BACKENDS.keys():
            try:
                async with app.ctx.http.get('%s/%s' % (url, "/health")) as resp:
                    if resp.status != 200:
                        RELAY_BACKENDS[url] = (int(time.time()), RELAY_BACKENDS[url][1] + 1)
                    elif url in RELAY_BACKENDS_BLOCK_LIST:
                        RELAY_BACKENDS_BLOCK_LIST.remove(url)
            except (CancelledError, ClientConnectorError) as e:
                RELAY_BACKENDS[url] = (int(time.time()), RELAY_BACKENDS[url][1] + 1)
                logger.exception(e)
            timestamp, count = RELAY_BACKENDS[url]
            if count > 0 and time.time() - timestamp < RELAY_BACKENDS_BLOCK_TIME:
                if url not in RELAY_BACKENDS_BLOCK_LIST:
                    RELAY_BACKENDS_BLOCK_LIST.append(url)
            elif count > 0 and time.time() - timestamp > RELAY_BACKENDS_INTERVAL:
                RELAY_BACKENDS[url] = (int(time.time()), 0)
        await asyncio.sleep(5)


@app.listener('before_server_start')
def init(app, loop):
    app.ctx.http = aiohttp.ClientSession(loop=loop, auto_decompress=False)


@app.listener('after_server_stop')
def finish(app, loop):
    loop.run_until_complete(app.ctx.http.close())
    loop.close()


async def forward(request, path, relay_backend, reply=True):
    headers = {}
    for key, value in request.headers.items():
        if key in ("host", "transfer-encoding", ):
            continue
        headers[key] = value
    async with app.ctx.http.request(    
        request.method,
        '%s/%s' % (relay_backend, path),
        params=request.args,
        data=request.body,
        headers=headers,
        cookies=request.cookies,
    ) as resp:
        if reply:
            response = await request.respond(status=resp.status, headers=resp.headers)
            async for chunk in resp.content.iter_any():
                await response.send(chunk)


@app.route(
    '/<path:path>',
    methods=["GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]
)
async def proxy(request, path):
    blocked = lambda url: url not in RELAY_BACKENDS_BLOCK_LIST
    if path in RELAY_PATHS:
        tasks = [
            forward(
                request,
                path,
                url,
                index == len(RELAY_BACKENDS) - 1,
            ) for index, url in enumerate(RELAY_BACKENDS.keys()) if blocked(url)
        ]
        if len(tasks) > 0:
            await asyncio.gather(*tasks)
        else:
            response = await request.respond(status=500)
            await response.send("no backend available")
    else:
        reply_backends = list(RELAY_BACKENDS.keys())
        reply_backends.sort(key=lambda url: RELAY_BACKENDS[url][1])
        await forward(request, path, reply_backends[0])


def waiting_for_backends():
    for url in RELAY_BACKENDS.keys():
        while True:
            try:
                with contextlib.closing(urlopen("%s/health" % url)) as response:
                    print(f"Connection to {url} succeeded, status: {response.status}")
                    break
            except BaseException:
                print(f"waiting %s backend..." % url)
            time.sleep(5)

if __name__ == '__main__':
    options, _ = getopt.getopt(
        sys.argv[1:],
        "h:p:w:",
        ["host=", "port=", "workers="]
    )
    host, port, workers = "0.0.0.0", 8000, 1
    for name, value in options:
        if name in ('-h', '--host'):
            host = value
        elif name in('-p', '--port'):
            port = int(value)
        elif name in('-w', '--workers'):
            workers = int(value)
    waiting_for_backends()
    app.add_task(check_health_task)
    app.run(host=host, port=port, workers=workers)
