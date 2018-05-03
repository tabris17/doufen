# encoding: utf-8

def test():
    import time, logging
    logging.debug('started')
    i = 0
    while True:
        i = i + 1
        time.sleep(2)
        received = yield i
        if isinstance(received, Test):
            logging.debug('Worker received:' + received.value)

class Test:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value