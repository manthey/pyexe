import multiprocessing
import random
import sys
import time
from six.moves import range


maxProcesses = 2
numJobs = 10


def calculateSum(idx, values, weight, results):
    sum = 0
    for value in values:
        sum += value * weight
        time.sleep(0.05)
    results[idx] = sum


if __name__ == '__main__':
    results = multiprocessing.Array('d', range(numJobs))
    multiprocessing.set_executable(sys.executable)
    jobs = []
    for i in range(numJobs):
        jobs.append((
            [random.random() for j in range(random.randint(10, 50))],
            random.random()
        ))
    procs = []
    for idx, job in enumerate(jobs):
        while len(multiprocessing.active_children()) >= maxProcesses:
            pass
        p = multiprocessing.Process(target=calculateSum, args=(idx, job[0], job[1], results))
        procs.append(p)
        p.start()
    while len(multiprocessing.active_children()) > 0:
        pass
    for p in procs:
        p.join()
    results = list(results)
    print('Multiprocess results: %r' % results)
    local = [sum([val * weight for val in values]) for values, weight in jobs]
    print('Direct results: %r' % local)
    print('Difference: (%g)\n' % round(sum(local) - sum(results), 10))
