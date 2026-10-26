import heapq
import sys
import threading

class Job:
    __slots__ = ('arrival', 'job_id', 'priority', 'duration', 'resources', 'seq')

    def __init__(self, arrival, job_id, priority, duration, resources, seq):
        self.arrival, self.job_id, self.priority = (arrival, job_id, priority)
        self.duration, self.resources, self.seq = (duration, resources, seq)

class JobDispatcher:

    def __init__(self):
        self._heap = []
        self._lock = threading.Lock()

    def submit(self, job):
        with self._lock:
            heapq.heappush(self._heap, (-job.priority, job.arrival, job.seq, job))

    def next_job(self):
        with self._lock:
            return heapq.heappop(self._heap)[3] if self._heap else None

    def has_jobs(self):
        with self._lock:
            return bool(self._heap)

def simulate(workers, jobs):
    jobs = sorted(jobs, key=lambda j: (j.arrival, j.seq))
    dispatcher = JobDispatcher()
    free = [(0, w) for w in range(1, workers + 1)]
    heapq.heapify(free)
    nxt, report, total_wait = (0, [], 0)
    done = 0
    while done < len(jobs):
        free_time, wid = free[0]
        t = free_time
        if not dispatcher.has_jobs():
            t = max(free_time, jobs[nxt].arrival)
        while nxt < len(jobs) and jobs[nxt].arrival <= t:
            dispatcher.submit(jobs[nxt])
            nxt += 1
        job = dispatcher.next_job()
        heapq.heappop(free)
        start, finish = (t, t + job.duration)
        heapq.heappush(free, (finish, wid))
        report.append((job, wid, start, finish))
        total_wait += start - job.arrival
        done += 1
    return (report, total_wait)

def main():
    data = sys.stdin.read().split()
    try:
        w, n = (int(data[0]), int(data[1]))
        if not (1 <= w <= 64 and 1 <= n):
            raise ValueError
        jobs = []
        for i in range(n):
            a, jid, pr, du, rs = data[2 + 5 * i:7 + 5 * i]
            job = Job(int(a), jid, int(pr), int(du), int(rs), i)
            if job.duration < 1 or job.arrival < 0:
                raise ValueError
            jobs.append(job)
    except (ValueError, IndexError):
        sys.exit('Invalid input format')
    report, total_wait = simulate(w, jobs)
    for job, wid, s, f in report:
        print(f'{job.job_id} W{wid} {s} {f}')
    print(f'AVG_WAIT {total_wait / n:.2f}')
if __name__ == '__main__':
    main()
