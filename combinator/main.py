import random
from cmd_args import tic, toc
from checker import boogie_result
import time

if __name__ == '__main__':
    random.seed(time.time())
    tic()
    boogie_result()
    print("time cost", toc())