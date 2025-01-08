# SuperFastPython.com
# example of checking for an exception raised in the task
from time import sleep
from multiprocessing.pool import Pool

# result callback function
def result_callback(result):
    print(result, flush=True)

# task executed in a worker process
def task(value):
    # block for a moment
    sleep(1)
    # check for failure case
    if value == 2:
        raise Exception('Something bad happened!')
    # report a value
    return value

# protect the entry point
if __name__ == '__main__':
    # create a process pool
    with Pool() as pool:
        # issue a task
        result = pool.apply_async(task, range(5), callback=result_callback)
        # wait for the task to finish
        result.wait()
        # check for a failure
        if result.successful():
            # get the result
            value = result.get()
            # report the result
            print(value)
        else:
            # report the failure case
            print('Unable to get the result')