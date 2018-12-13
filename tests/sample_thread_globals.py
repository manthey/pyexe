# Thread function with globals

import threading
import time


def threaded_func():
    time.sleep(1)
    print(globalVar)


globalVar = "Global Variable"
threading.Thread(target=threaded_func).start()
