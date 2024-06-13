import random
import json
import time
import numpy as np
from copy import copy, deepcopy
from stqdm import stqdm
from itertools import permutations
from itertools import takewhile
from matplotlib import pyplot as plt
from utils import *

POPSIZE =  200
CROSSOVER_RATE = 0.6
MUTATION_RATE = 0.1

class Individual:
    def __init__(self, processing_times, n, m):
        permutation = [i for i in range(n*m)]
        self.code = [-1 for i in range(n*m)]
        for i in range(n*m):
            self.code[i] = random.choice(permutation)
            permutation.remove(self.code[i])

        self.fitness = self.calc_fitness(processing_times,n,m)

    def check_job(self, start, limit, duration, job_activity):
        if len(job_activity) == 0:
            if start+duration<=limit:
                return (True, start) 
        elif len(job_activity) == 1:
            if job_activity[0][0] !=0 and job_activity[0][0]>=start+duration:
                return (True, start) 
            else:
                if job_activity[0][1] + duration <= limit:
                    return (True, max(job_activity[0][1],start)) 
        else:
            end = start + duration
            j=0
            while end <= limit and j<len(job_activity)-1:
                if job_activity[j][0] <= start < job_activity[j][1]:
                    start = job_activity[j][1]
                    end = start + duration
                    
                if start >= job_activity[j][1] and end <= job_activity[j+1][0]:        
                    return (True, start)
             
                j+=1
            
        return (False, -1)

    def calc_fitness(self, processing_times, n, m):
        jobs = [[] for _ in range(n)]
        machines = [[] for _ in range(m)]
        for operation in self.code:
                machine = operation % n
                job = operation // n
                duration = processing_times[job][machine]
                machine_activity = machines[machine]
                job_activity = jobs[job]
                
                fit, start, limit = False, -1, float('inf')
                if len(machine_activity) == 0:
                    start=0
                    fit, start = self.check_job(start, limit, duration, job_activity)
                elif len(machine_activity) == 1 and machine_activity[0][0] !=0:
                    start = 0
                    limit = machine_activity[0][0]
                    fit, start = self.check_job(start, limit, duration, job_activity)
                elif len(machine_activity) == 1 and machine_activity[0][0] == 0:
                    start = machine_activity[0][1]
                    fit, start = self.check_job(start, limit, duration, job_activity)
                else:
                    for i in range(len(machine_activity) - 1):
                        start = machine_activity[i][1]
                        limit = machine_activity[i+1][0]
                        options=[]
                        if limit-start>=duration:
                            fit, start = self.check_job(start, limit, duration, job_activity)
                            if fit:
                                options.append((start, limit-(start+duration)))
                    if len(options)>0:
                        options.sort(key=lambda x: x[1])
                        start = options[0][0]
                        fit = True
                            
                if fit and start+duration<=limit:
                    jobs[job].append((start, start+duration))
                    machines[machine].append((start, start+duration))
                    jobs[job].sort()
                    machines[machine].sort()
                else:
                    start=0
                    if len(machine_activity)>=1:
                        start = machine_activity[-1][1]
                    if len(job_activity)>=1:
                        start = max(start, job_activity[-1][1])
                    jobs[job].append((start, start+duration))
                    machines[machine].append((start, start+duration))
        
        
        for machine in machines:
            machine.sort(key=lambda x: x[1], reverse=True)
        return max([machine[0][1] for machine in machines])
    


# generational genetic algorithm
# uniform crossover with rate 0.6,
# swap mutation with rate 0.1
# roulette wheel selection (size of the slot on the roulette is inversly proportional to the fitness value (makespan) of each chromosome)
# 500 generations with 200 chromosomes


def selection(population):
    population_fitness = sum([1/chromosome.fitness for chromosome in population])
    
    chromosome_probabilities = [(1/(chromosome.fitness)/population_fitness) for chromosome in population]
    
    parents = random.choices(population, weights=chromosome_probabilities, k=2)
   
    return (parents[0], parents[1])

def crossover (parent1, parent2, child1, child2):
    code1 = [-1]*len(child1.code)
    code2 = [-1]*len(child1.code)
    p1 = parent1.code.copy()
    p2 = parent2.code.copy()
    for i in range(len(parent1.code)):
        if random.random()<0.5:
            code1[i]=parent1.code[i]
            p2.remove(parent1.code[i])
            code2[i]=parent2.code[i]
            p1.remove(parent2.code[i])
    j=0
    for i in range(len(code1)):
        if code1[i]==-1:
            code1[i]=p2[j]
            code2[i]=p1[j]
            j+=1

    child1.code = code1.copy()
    child2.code = code2.copy()
    
def mutation (child, rate):
    i = random.randrange(0,len(child.code))
    j=i
    while j==i:
        j = random.randrange(0,len(child.code))
    child.code[i], child.code[j] = child.code[j], child.code[i]

def ga_permutation(pop_size, num_iters, crossover_rate, mutation_rate, elitism_size, n, m, processing_times):
    
    if (pop_size - elitism_size) % 2 == 1:
        elitism_size += 1
    
    population = [Individual(processing_times, n, m) for _ in range(pop_size)]
    new_population =[ Individual(processing_times, n, m) for _ in range(pop_size)]
    
    for _ in range(num_iters):
            
        population.sort(key=lambda x: x.fitness)  
        new_population[:elitism_size] = population[:elitism_size]
        
        for i in range(elitism_size, pop_size, 2):
            parent1, parent2 = selection(population)
            
            if random.random() < crossover_rate:
                crossover(parent1, parent2,
                      new_population[i],
                      new_population[i+1])
            
            mutation(new_population[i], mutation_rate)
            mutation(new_population[i+1], mutation_rate)
            
            new_population[i].fitness = new_population[i].calc_fitness(processing_times, n, m)
            new_population[i+1].fitness = new_population[i+1].calc_fitness(processing_times, n, m)
        
        population = deepcopy(new_population)
            
    best_individual = min(population, key=lambda x: x.fitness)
    return best_individual.code, best_individual.fitness




def run_genetic_algorithm(n,m,processing_times,ub=0,lb=0, num_iters=500,pop_size=POPSIZE,crossover_rate=CROSSOVER_RATE,mutation_rate=MUTATION_RATE):
    elitism_size = int(0.2*pop_size)
    datas = []
    results = [[] for _ in range(10)]
    for i in range(1):
        start_time = time.time()
        j=0
        for it in stqdm(range(100)):
            results[i].append(ga_permutation(pop_size, num_iters, crossover_rate, mutation_rate, elitism_size, n, m, processing_times))
            j+=1
        end_time = time.time()
        sequence,mspan = min(results[i])
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


def run_genetic_algorithm_tests(n,m,num_iters=500,pop_size=POPSIZE,mutation_rate=MUTATION_RATE,crossover_rate=CROSSOVER_RATE,save_location="results"):
    elitism_size = int(0.2*pop_size)
    
    datas = []
    test_name=f"test{n}{m}"
    bounds = [(0,0) for _ in range(10)]
    results = [[] for _ in range(10)]
    for i in range(10):
        instance_file = f"tests/{test_name}{str(i)}"
        n, m, processing_times, ub, lb = read_instance(instance_file)
        start_time = time.time()
        j=0
        for it in stqdm(range(100),desc=f"Genetic: J{n}M{m} Population:{pop_size} Mutation rate:{mutation_rate} "):
            results[i].append(ga_permutation(pop_size, num_iters, crossover_rate, mutation_rate, elitism_size, n, m, processing_times))
            j+=1
        end_time = time.time()
        sequence,mspan = min(results[i])
        datas.append({
            'n': int(n),  # Convert to int if n is a numpy int64
            'm': int(m),  # Convert to int if m is a numpy int64
            'upperbound': int(ub),  # Convert to int if ub is a numpy int64
            'lowerbound': int(lb),  # Convert to int if lb is a numpy int64
            'processing_times': [[int(time) for time in times] for times in processing_times],  # Convert each time if they are numpy int64
            'makespan': int(mspan),  # Convert to int if mspan is a numpy int64
            'sequence': [int(seq) for seq in sequence],
            'runtime':end_time-start_time,
        })
    best = [min([results[i][j][1] for j in range(len(results[i]))]) for i in range(10)]
    mean = [int(sum([results[i][j][1] for j in range(len(results[i]))])/(len(results[i]))) for i in range(10)]
    for i in range(10):
        datas[i]['makespan']=int(best[i])
        datas[i]['mean']=int(mean[i])
    with open(f"{save_location}/genetic_"+test_name+'.json', 'w') as f:
        json.dump(datas, f)



# def display_images_ga(n,m):
#     genetic_results = load_genetic_data(n,m)
#     for i,result in enumerate(genetic_results):
#         n=result['n']
#         m=result['m']
#         processing_times=result['processing_times']
#         sequence=result['sequence']
#         visualize_schedule("Genetic",i,n,m,sequence,processing_times)

# def display_stat_ga(n,m):
#     genetic_results = load_genetic_data(n,m)
#     plt.plot(range(10), [result['lowerbound'] for result in genetic_results],label="Lower Bound",color='red')
#     plt.plot(range(10), [result['upperbound'] for result in genetic_results],label="Upper Bound",color='green')
#     plt.plot(range(10), [result['makespan'] for result in genetic_results],label="Best",color='blue')
#     plt.xlabel('Index')
#     plt.ylabel('Value')
#     plt.title(f"Genetic Algorithm: Plot of Bounds and Mean J:{n}M:{m}")
#     plt.legend()
#     plt.show()

# def run_well_known_test_ga(iteration=500):
#     pop_size =  POPSIZE
#     num_iters =  iteration
#     crossover_rate = CROSSOVER_RATE
#     mutation_rate = MUTATION_RATE
#     elitism_size = int(0.2*pop_size)
#     instance_file = f"tests/wellknowntest"
#     results = [[] for _ in range(10)]
#     n, m, processing_times, ub, lb = read_instance(instance_file)
#     j=0
#     for it in stqdm(range(100)):
#         results[0].append(ga_permutation(pop_size, num_iters, crossover_rate, mutation_rate, elitism_size, n, m, processing_times))
#         j+=1
#     sequence,mspan = min(results[0])
#     visualize_schedule("Genetic",-1,n,m,sequence,processing_times)


