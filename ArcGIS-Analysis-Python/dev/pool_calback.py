# SuperFastPython.com
# example of parallel starmap_async() with the process pool and a callback function
from random import random
from time import sleep
from multiprocessing.pool import Pool

import traceback
import arcpy

# custom error callback function
def custom_error_callback(error):
    arcpy.AddError(f'Error Callback: {error}')

# custom callback function
def custom_callback(result):
    arcpy.AddMessage(f'\tResult: {result}')

# task executed in a worker process
def task(identifier, value):
    try:
        # report a message
        #print(f'Task {identifier} executing with {value}', flush=True)
        # block for a moment
        sleep(value)

        # check for failure case
        if identifier == 4:
            raise Exception(f'Something bad happened with {identifier}!')
        else:
            arcpy.AddMessage(f'Task {identifier} executing with {value}')

        # return the generated value
        return (identifier, value)
    except:
        if traceback.print_exc():
            raise Exception(traceback.print_exc())
        else:
            raise Exception

# protect the entry point
if __name__ == '__main__':
    try:
        # create and configure the process pool
        with Pool() as pool:
            # prepare arguments
            items = [(i, random()) for i in range(10)]

            jobs={}
            for i in range(0, len(items)):
                #print(f"Processing: {items[i]}")

                #jobs[items[i]] = pool.apply_async(task, items[i], callback=custom_callback, error_callback=custom_error_callback)
                jobs[items[i]] = pool.apply_async(task, items[i], error_callback=custom_error_callback)
                #jobs[items[i]] = pool.starmap_async(task, [items[i]], error_callback=custom_error_callback)

                del i


            for identifier, job_result in jobs.items():

                worker_results = ""

                try:
                    worker_results = job_result.get()
                    #arcpy.AddMessage(worker_results)

                except Exception as e:
                    pool.terminate()

                    if e:
                        raise Exception(e)
                    else:
                        raise Exception

    ##        # issues tasks to process pool
    ##        _ = pool.starmap_async(task, items, callback=custom_callback, error_callback=custom_error_callback)
    ##        # close the process pool
            pool.close()
            # wait for all tasks to complete and processes to close
            pool.join()

    except Exception:
        pass
    except:
        traceback.print_exc()