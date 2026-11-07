import math, random, heapq

def erlang(arrival, service, c):
    offered = arrival / service
    rho = offered / c
    if rho >= 1:
        raise ValueError('Unstable capacity: arrival must be below total service capacity')
    term = 1.0
    total = 1.0
    for k in range(1, c):
        term *= offered / k
        total += term
    tail = term * offered / c / (1 - rho)
    wait = tail / (total + tail)
    return {'utilization': rho, 'probability_wait': wait, 'mean_queue_wait_seconds': wait / (c * service - arrival), 'mean_response_seconds': 1 / service + wait / (c * service - arrival)}

def percentile(values, q):
    s = sorted(values)
    return s[min(len(s) - 1, math.ceil(q * len(s)) - 1)]

def simulate(arrival, service, c, jobs, seed):
    rng = random.Random(seed)
    workers = [0.0] * c
    heapq.heapify(workers)
    clock = 0.0
    waits = []
    responses = []
    for _ in range(jobs):
        clock += rng.expovariate(arrival)
        available = heapq.heappop(workers)
        start = max(clock, available)
        duration = rng.expovariate(service)
        heapq.heappush(workers, start + duration)
        waits.append(start - clock)
        responses.append(start - clock + duration)
    return {'jobs': jobs, 'mean_queue_wait_seconds': sum(waits) / jobs, 'p95_queue_wait_seconds': percentile(waits, 0.95), 'p95_response_seconds': percentile(responses, 0.95), 'seed': seed}

def run(p):
    arrival = p.get('arrival_per_second', 8.0)
    service = p.get('service_per_worker_second', 3.0)
    target = p.get('max_wait_seconds', 0.5)
    allowed = p.get('max_wait_breach_probability', 0.05)
    cost = p.get('hourly_cost_per_worker', 0.04)
    jobs = p.get('simulation_jobs', 5000)
    if any((type(v) not in [int, float] or not math.isfinite(v) for v in [arrival, service, target, allowed, cost])) or arrival <= 0 or service <= 0 or (target < 0) or (not 0 < allowed < 1) or (cost < 0):
        raise ValueError('Finite positive rates, nonnegative costs/wait, and probability between 0 and 1 required')
    if not isinstance(jobs, int) or not 100 <= jobs <= 50000:
        raise ValueError('simulation_jobs must be 100–50000')
    candidates = []
    for c in range(1, 101):
        if c * service <= arrival:
            continue
        metric = erlang(arrival, service, c)
        breach = metric['probability_wait'] * math.exp(-(c * service - arrival) * target)
        candidates.append(dict(workers=c, hourly_cost=c * cost, wait_breach_probability=breach, **metric))
        if breach <= allowed:
            return {'recommended': candidates[-1], 'simulation': simulate(arrival, service, c, jobs, p.get('seed', 42)), 'candidates': candidates, 'assumption': 'M/M/c; supplied costs, not live provider prices'}
    raise ValueError('No solution within the 100-worker search cap')
