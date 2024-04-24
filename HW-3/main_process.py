from multiprocessing import Pool, cpu_count
from time import time, sleep


def factorize(*number):
    s = []
    for num in number:
        n = []
        for i in range(1, num+1):
            if num % i == 0:
                n.append(i)
        s.append(n)
    return s


def factorize_one(num):
    n = []
    for i in range(1, num+1):
        if num % i == 0:
            n.append(i)
    return n


def factorize_many(*number):
    with Pool(cpu_count()) as pool:
        return pool.map(factorize_one, number)


if __name__ == "__main__":

    timer = time()
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    print(f"Час виконання функції {round(time() - timer, 5)} секунд")

    sleep(5)

    timer = time()
    a1, b1, c1, d1 = factorize_many(128, 255, 99999, 10651060)
    print(f"Час виконання потоків {round(time() - timer, 5)} секунд")

    # assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    # assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    # assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    # assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]
