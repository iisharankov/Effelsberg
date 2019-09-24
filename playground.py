
#
#
# # print(type(humanData))
# # print(humanData['people'][0]['Name'])
# #
# # newHumanData = json.dumps(humanData)
# # print(type(newHumanData))
#
#
# #
# # while True:
# #     print(1)
# #     while True:
# #         print(2)
# #         break
# #     print(3)
# #     break
#

import logging
import threading
import time


def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,), daemon=True)
    logging.info("Main    : before running thread")
    x.start()
    logging.info("Main    : wait for the thread to finish")
    # x.join()
    logging.info("Main    : all done")
