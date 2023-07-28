# from threading import Thread
#
# # from telegram.bot import run_bot
# import logging
# import asyncio
# from reestr_parser.runner import cmd_crawl, run_spider
#
#
# def setup_logger(logger_name, logfile):
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(logging.INFO)
#     # create file handler which logs even debug messages
#     fh = logging.FileHandler(logfile)
#     fh.setLevel(logging.INFO)
#     # create console handler with a higher log level
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.DEBUG)
#     # create formatter and add it to the handlers
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     fh.setFormatter(formatter)
#     ch.setFormatter(formatter)
#     # add the handlers to the logger
#     logger.addHandler(fh)
#     logger.addHandler(ch)
#     return logger
#
#
# async def main():
#
#     await run_bot()
#
#
# async def crawl():
#     run_spider()
#     #aioschedule.every().day.at("10:30", "Europe/Moscow").do(run_spider)
#     aioschedule.every(10).minutes.do(run_spider)
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(1)
#
#
# if __name__ == "__main__":
#     logger = setup_logger('logger', 'log.log')
#     logger.info("Logger has been initialized")
#
#     try:
#         asyncio.run(main())
#     except (KeyboardInterrupt, SystemExit):
#         logging.error("Bot stopped!")
#
#     #thread.join()
