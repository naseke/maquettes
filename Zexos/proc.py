import time
import multiprocessing

def truc(nb):
    time.sleep(0.5)
    print(f'truc-{nb}')
    time.sleep(5)
    print(f'truc2-{nb}')


def main():
    p = multiprocessing.Pool(5)
    for i in range(100):
        print(i)
        result = p.apply_async(truc, [i])
        #print(result.get(timeout=1))

    p.close()
    p.join()


if __name__ == '__main__':
    main()
