import asyncio

from loguru import logger

from get_proxies import update_proxies


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(update_proxies())
    except KeyboardInterrupt:
        logger.info('Script stopped')
