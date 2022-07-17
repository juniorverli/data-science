import numpy as np
from timeit import default_timer as timer
#from numba import vectorize

#@vectorize(["float32(float32,float32)"], target='cpu')

def vectorAdd(a,b):
    return a + b


def main():
    N = 32000000

    A = np.ones(N, dtype=np.float32)
    B = np.ones(N, dtype=np.float32)
    C = np.zeros(N, dtype=np.float32)

    start = timer()
    vectorAdd(A,B)
    vectoraddtime = timer() - start
    print ("C[:5] = " + str(C[:5]))
    print ("C[-5:] = " + str(C[-5:]))

    print("VectorAdd took %f seconds" % vectoraddtime)

if __name__ == '__main__':
    main()