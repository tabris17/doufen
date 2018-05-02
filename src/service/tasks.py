# encoding: utf-8

def test():
    import time, logging
    logging.debug('started')
    i = 0
    while True:
        i = i + 1
        time.sleep(2)
        received = yield i
        logging.debug(received)

