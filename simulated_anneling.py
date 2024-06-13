import random
import json
import time
import numpy as np
from copy import copy, deepcopy
from itertools import permutations, takewhile
from utils import *
from stqdm import stqdm

def makespan(scheduling, processing_times):
    n = len(scheduling[0])
    m = len(scheduling)
    permutation=[]

    jobs = [Job(i, processing_times[i]) for i in range(n)]
    machines = [Machine(j, processing_times) for j in range(m)]

    for j in range(n):
        machine_candidates = list(takewhile(lambda m: m.time_available == machines[0].time_available, machines))
        if len(machine_candidates)>1:
            machine_candidates.sort(key = lambda m: m.remaining_time, reverse=True)
            machine_candidates = list(takewhile(lambda m: m.remaining_time == machine_candidates[0].remaining_time, machine_candidates))
            if len(machine_candidates)>1:
                job_candidates = [-1 for _ in range(m)]
                for machine in machine_candidates:
                    job_candidates[machine.id] = scheduling[machine.id][j]
                machine_candidates.sort(key = lambda m: jobs[job_candidates[m.id]].remaining_time - processing_times[job_candidates[m.id]][m.id], reverse=True)
        candidates_ids= [machine.id for machine in machine_candidates]
        machines = machine_candidates + [machine for machine in machines if machine.id not in candidates_ids]
        for machine in machines:
            permutation.append(jobs[scheduling[machine.id][j]].id*n+machine.id)
            update(machine, jobs[scheduling[machine.id][j]], processing_times)
            
        machines.sort(key = lambda m: m.time_available)
       
    return (np.max([machine.time_available for machine in machines]), permutation)


class Job():

    def __init__(self, job_id, processing_times):
        self.id = job_id
        self.processing_times = processing_times
        self.time_available = 0
        self.remaining_time = sum(processing_times)
        self.remaining_machines = set([i for i in range(len(processing_times))])
        
class Machine():
    def __init__(self, machine_id, processing_times):
        self.id = machine_id
        self.time_available = 0
        self.remaining_time = sum([processing_times[i][machine_id] for i in range(len(processing_times[0]))])
        self.remaining_jobs = set([i for i in range(len(processing_times[0]))])

def update(machine, job, processing_times):
    duration = processing_times[job.id][machine.id]
    end  = max(machine.time_available, job.time_available) + duration
    machine.remaining_time -= duration
    machine.remaining_jobs.remove(job.id)
    machine.time_available = end
    job.remaining_time -= duration
    job.remaining_machines.remove(machine.id)
    job.time_available = end


def scheduling(processing_times):
    n = len(processing_times)
    m = len(processing_times[0])
    schedule = [[0]*n for _ in range(m)]
    
    jobs = [Job(i, processing_times[i]) for i in range(n)]
    machines = [Machine(j, processing_times) for j in range(m)]
    
    next_machine_candidates = copy(machines)
    next_machine_candidates.sort(key = lambda m: m.remaining_time, reverse=True)
    first_machine = next_machine_candidates[0]
    job_candidates = copy(jobs)
    job_candidates.sort(key = lambda job: job.remaining_time - processing_times[job.id][first_machine.id], reverse=True)
    first_job = job_candidates[0]
    schedule[first_machine.id][0] = first_job.id
    update(first_machine, first_job, processing_times)
    
    for k in range(1, n*m):

        next_machine_candidates.sort(key = lambda m: m.time_available)
       
        next_job_candidates = []
        for next_machine in next_machine_candidates:
            job_candidates = []
            for job in next_machine.remaining_jobs:
                if jobs[job].time_available<=next_machine.time_available:
                    job_candidates.append((jobs[job],jobs[job].remaining_time-jobs[job].processing_times[next_machine.id]))
            if len(job_candidates)!=0:
                next_machine_id = next_machine.id
                next_job_candidates = copy(job_candidates)
                break
        if len(next_job_candidates)==0:
            for machine in next_machine_candidates: 
                if len(machine.remaining_jobs)!=0:
                    next_machine_id=machine.id
                    break
            remaining_jobs = list(machines[next_machine_id].remaining_jobs)
            remaining_jobs.sort(key = lambda job: jobs[job].remaining_time-jobs[job].processing_times[next_machine_id], reverse=True)
            job = remaining_jobs[0]
            next_job_candidates.append((jobs[job], jobs[job].remaining_time-jobs[job].processing_times[next_machine_id]))
    
        else:
            next_job_candidates.sort(key = lambda job: job[1], reverse=True)

        next_job = next_job_candidates[0][0]
        next_machine = machines[next_machine_id]
        schedule[next_machine.id][len(processing_times)-len(next_machine.remaining_jobs)] = next_job.id
        update(next_machine, next_job, processing_times)
        
    return schedule



def swap_operations(schedule):
    neighbor = deepcopy(schedule)
    row = random.choice(range(len(schedule)))
    col1, col2 = random.sample(range(len(schedule[0])),2)
    schedule[row][col1], schedule[row][col2] = schedule[row][col2], schedule[row][col1]
    
    return schedule

def simulated_annealing(n, m, processing_times, max_iters):
    solution = scheduling(processing_times)
    value = makespan(solution,processing_times)[0]
    best_solution = deepcopy(solution)
    best_value = value
    
    for i in (range(1, max_iters)):

        new_solution = swap_operations(solution)
        
        new_value = makespan(new_solution, processing_times)[0]
        
        if new_value < value:
            value = new_value
            solution = new_solution
            if new_value < best_value:
                best_value = new_value
                best_solution = deepcopy(new_solution)
        else:
            p = 1 / i**0.5 
            q = random.random()
            if q < p:
                value = new_value
                solution = new_solution
                
    return makespan(best_solution, processing_times)


def run_simulated_anneling(n,m,processing_times,ub=0,lb=0,iterations=100000):
    datas = []
    test_name=f"test{n}{m}"
    bounds = [(0,0) for _ in range(10)]
    results = [[] for _ in range(10)]
    for i in range(1):
        start_time = time.time()
        j=0
        for it in stqdm(range(100)):
            results[i].append(simulated_annealing(n, m, processing_times, iterations))
            j+=1
        end_time = time.time()
        mspan,sequence  = min(results[i])
        datas.append({
            'n': int(n),  # Convert to int if n is a numpy int64
            'm': int(m),  # Convert to int if m is a numpy int64
            'upperbound': int(ub),  # Convert to int if ub is a numpy int64
            'lowerbound': int(lb),  # Convert to int if lb is a numpy int64
            'processing_times': [[int(time) for time in times] for times in processing_times],  # Convert each time if they are numpy int64
            'makespan': int(mspan),  # Convert to int if mspan is a numpy int64
            'sequence': [int(seq) for seq in sequence],
            'runtime':end_time - start_time
        })
    return datas[0]


def run_simulated_anneling_tests(n,m,iterations=100000,save_location="results"):
    datas = []
    test_name=f"test{n}{m}"
    bounds = [(0,0) for _ in range(10)]
    results = [[] for _ in range(10)]
    for i in range(10):
        instance_file = f"tests/{test_name}{str(i)}"
        n, m, processing_times, ub, lb = read_instance(instance_file)

        start_time = time.time()
        j=0
        for it in stqdm(range(100),desc=f"Simulated Annealing: J{n}M{m} "):
            results[i].append(simulated_annealing(n, m, processing_times, iterations))
            j+=1
        end_time = time.time()
        mspan,sequence  = min(results[i])
        datas.append({
            'n': int(n),  # Convert to int if n is a numpy int64
            'm': int(m),  # Convert to int if m is a numpy int64
            'upperbound': int(ub),  # Convert to int if ub is a numpy int64
            'lowerbound': int(lb),  # Convert to int if lb is a numpy int64
            'processing_times': [[int(time) for time in times] for times in processing_times],  # Convert each time if they are numpy int64
            'makespan': int(mspan),  # Convert to int if mspan is a numpy int64
            'sequence': [int(seq) for seq in sequence],
            'runtime':end_time - start_time
        })

    best = [min([results[i][j][0] for j in range(len(results[i]))]) for i in range(10)]
    mean = [int(sum([results[i][j][0] for j in range(len(results[i]))])/(len(results[i]))) for i in range(10)]
    for i in range(10):
        datas[i]['makespan']=int(best[i])
        datas[i]['mean']=int(mean[i])
    
    with open(f"{save_location}/simulated_anneling_"+test_name+'.json', 'w') as f:
        json.dump(datas, f)

