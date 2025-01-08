import multiprocessing

def square(x):
    return x * x

if __name__ == '__main__':
    with multiprocessing.Pool() as pool:
        numbers = [1, 2, 3, 4, 5]
        result = pool.map(square, numbers)

    print(result)  # Output: [1, 4, 9, 16, 25]