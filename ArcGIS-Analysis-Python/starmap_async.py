# SuperFastPython.com
# example of parallel starmap_async() with the process pool
from random import random
from time import sleep
from multiprocessing.pool import Pool

# custom callback function
def custom_callback(result):
    print(f'Callback got values: {result}', flush=True)

# custom error callback function
def custom_error_callback(error):
    print(f'Got an error: {error}', flush=True)

# task executed in a worker process
def task(identifier, value):
    # conditionally raise an error
    #if identifier == 25:
    #    raise Exception('Something bad happened')
    # report a message
    #print(f'Task {identifier} executing with {value}', flush=True)
    # block for a moment
    sleep(value)
    # return the generated value
    return (identifier, value)

# protect the entry point
if __name__ == '__main__':
    # create and configure the process pool
    with Pool() as pool:
        # prepare arguments
        items = [(i, random()) for i in range(100)]
        # issues tasks to process pool
        result = pool.starmap_async(task, items)
        #result = pool.starmap_async(task, items, error_callback=custom_error_callback)
        #result = pool.starmap_async(task, items, callback=custom_callback)
        #result = pool.starmap_async(task, items, callback=custom_callback, error_callback=custom_error_callback)
        try:
            # iterate results
            for result in result.get():
                print(f'Got result: {result}', flush=True)
        except Exception as e:
            print(f'Failed with: {e}')

        # get the return values
        #try:
        #    values = result.get()
        #except Exception as e:
        #    print(f'Failed with: {e}')
    # process pool is closed automatically