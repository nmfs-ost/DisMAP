# SuperFastPython.com
# example in a callback function for the process pool
from time import sleep
from multiprocessing.pool import Pool

# callback function
def handler(result):
    # report result
    print(f'Got result {result}', flush=True)
    # fail with an exception
    raise Exception('Something bad happened!')

# task executed in a worker process
def task():
    # block for a moment
    sleep(1)
    # return a value
    return 22

# protect the entry point
if __name__ == '__main__':
    # create a process pool
    with Pool() as pool:
        # issue a task to the process pool
        result = pool.apply_async(task, callback=handler)
        # wait for the task to finish
        result.wait()