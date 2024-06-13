import random
import time
import numpy as np
from stqdm import stqdm
from itertools import takewhile
from copy import copy
from copy import deepcopy
from matplotlib import pyplot as plt
import json
from utils import *

TABU_LENGTH = 6

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
        self.remaining_jobs = set([i for i in range(len(processing_times))])


def update(machine, job, processing_times):
    duration = processing_times[job.id][machine.id]
    end  = max(machine.time_available, job.time_available) + duration
    machine.remaining_time -= duration
    machine.remaining_jobs.remove(job.id)
    machine.time_available = end
    job.remaining_time -= duration
    job.remaining_machines.remove(machine.id)
    job.time_available = end

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







def pairwise_exchange_neighborhood(schedule):
    n = len(schedule[0])
    m = len(schedule)
    neighborhood = []
    for i in range(m):
        for j in range(n):
            for k in range(i, n):
                    if j == k:
                        continue
                    neighbor = deepcopy(schedule)
                    neighbor[i][j], neighbor[i][k] = neighbor[i][k], neighbor[i][j]
                    neighborhood.append(neighbor)
    return neighborhood



def tabu_search(n, m, processing_times, tabu_length, max_iterations, initial_solution, upper_bound):
    best_solution = initial_solution
    best_makespan = makespan(initial_solution, processing_times)[0]
    current_solution = initial_solution
    tabu_list = []
    for it in stqdm(range(max_iterations),desc=f"Tabu Search: J{n}M{m} Tabu length:{tabu_length} "):
        neighborhood = pairwise_exchange_neighborhood(current_solution)
        best_neighbor = neighborhood[0]
        best_neighbor_makespan = makespan(best_neighbor, processing_times)[0]
        for neighbor in neighborhood[1:]:
            neighbor_makespan = makespan(neighbor, processing_times)[0]
            if neighbor_makespan < best_neighbor_makespan and neighbor not in tabu_list:
                best_neighbor = neighbor
                best_neighbor_makespan = neighbor_makespan
        current_solution = best_neighbor
        if best_neighbor_makespan < best_makespan:
            best_solution = best_neighbor
            best_makespan = best_neighbor_makespan
        tabu_list.append(best_neighbor)
        if len(tabu_list) > tabu_length:
            tabu_list.pop(0)
    return makespan(best_solution, processing_times)




def run_tabu_search(n,m,processing_times,ub=0,lb=0,tabu_length=TABU_LENGTH, iterations=10000):
    datas = []
    start_time=time.time()
    mspan, sequence = tabu_search(n, m, processing_times, TABU_LENGTH, iterations, scheduling(processing_times), ub)
    end_time=time.time()
    datas.append({
        'n': int(n),  # Convert to int if n is a numpy int64
        'm': int(m),  # Convert to int if m is a numpy int64
        'upperbound': int(ub),  # Convert to int if ub is a numpy int64
        'lowerbound': int(lb),  # Convert to int if lb is a numpy int64
        'processing_times': [[int(time) for time in times] for times in processing_times],  # Convert each time if they are numpy int64
        'makespan': int(mspan),  # Convert to int if mspan is a numpy int64
        'sequence': [int(seq) for seq in sequence],
        'runtime':end_time-start_time
    })
    return datas[0]


def run_tabu_search_tests(n,m,iterations=10000,save_location="results"):
    datas = []
    test_name=f"test{n}{m}"
    for i in range(10):
        instance_file = f"tests/{test_name}{str(i)}"
        n, m, processing_times, ub, lb = read_instance(instance_file)
        start_time = time.time()
        mspan, sequence = tabu_search(n, m, processing_times, TABU_LENGTH, iterations, scheduling(processing_times), ub)
        end_time = time.time()

        datas.append({
            'n': int(n),  # Convert to int if n is a numpy int64
            'm': int(m),  # Convert to int if m is a numpy int64
            'upperbound': int(ub),  # Convert to int if ub is a numpy int64
            'lowerbound': int(lb),  # Convert to int if lb is a numpy int64
            'processing_times': [[int(time) for time in times] for times in processing_times],  # Convert each time if they are numpy int64
            'makespan': int(mspan),  # Convert to int if mspan is a numpy int64
            'sequence': [int(seq) for seq in sequence],  # Convert each sequence element if they are numpy int64
            'runtime':end_time-start_time
        })

    with open(f"{save_location}/tabu_"+test_name+'.json', 'w') as f:
        json.dump(datas, f)














