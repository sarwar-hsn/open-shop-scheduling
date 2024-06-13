import json
import numpy as np
from matplotlib import pyplot as plt


TABU_SEARCH = 'TABU_SEARCH'
SIMULATED_ANNEALING = 'SIMULATED_ANNEALING'
GENETIC_ALGORITHM = 'GENETIC_ALGORITHM'

def load_tabu_data(n,m,load_location="results"):
    with open(f"{load_location}/tabu_test{n}{m}.json", 'r') as f:
        data = json.load(f)
    return data

def load_genetic_data(n,m,load_location="results"):
    with open(f"{load_location}/genetic_test{n}{m}.json", 'r') as f:
        data = json.load(f)
    return data


def load_simulated_anneling_data(n,m,load_location="results"):
    with open(f"{load_location}/simulated_anneling_test{n}{m}.json", 'r') as f:
        data = json.load(f)
    return data

def display_stat_makespan_single_algorithm(algorithm, n, m,load_location="results"):
    if algorithm == TABU_SEARCH:
        results = load_tabu_data(n, m,load_location=load_location)
    elif algorithm == SIMULATED_ANNEALING:
        results = load_simulated_anneling_data(n, m,load_location=load_location)
    else:
        results = load_genetic_data(n, m,load_location=load_location)

    fig, ax = plt.subplots()
    ax.plot(range(10), [result['lowerbound'] for result in results], label="Lower Bound", color='red')
    ax.plot(range(10), [result['upperbound'] for result in results], label="Upper Bound", color='green')
    ax.plot(range(10), [result['makespan'] for result in results], label="Best", color='blue')
    ax.set_xlabel('Tests')
    ax.set_ylabel('Bounds')
    ax.set_title(f"{algorithm.capitalize()}: Plot of Bounds and Makespan J:{n}M:{m}")
    ax.legend()
    return fig


def display_stat_makespan_all_algorithm(n, m,load_location="results"):
    ts_results = load_tabu_data(n, m,load_location=load_location)
    sa_results = load_simulated_anneling_data(n, m,load_location=load_location)
    ga_results = load_genetic_data(n, m,load_location=load_location)

    fig, ax = plt.subplots()
    ax.plot(range(10), [result['makespan'] for result in ts_results], label="Tabu Search", color='blue')
    ax.plot(range(10), [result['makespan'] for result in sa_results], label="Simulated Annealing", color='red')
    ax.plot(range(10), [result['makespan'] for result in ga_results], label="Genetic Algorithm", color='green')
    ax.set_xlabel('Tests')
    ax.set_ylabel('Makespan')
    ax.set_title(f"Plot of Makespan Analysis J:{n}M:{m}")
    ax.legend()
    return fig




def display_stat_runtime(n, m,load_location="results"):
    ts_results = load_tabu_data(n, m,load_location=load_location)
    sa_results = load_simulated_anneling_data(n, m,load_location=load_location)
    ga_results = load_genetic_data(n, m,load_location=load_location)

    fig, ax = plt.subplots()
    ax.plot(range(10), [result['runtime'] for result in ts_results], label="Tabu Search", color='blue')
    ax.plot(range(10), [result['runtime'] for result in sa_results], label="Simulated Annealing", color='red')
    ax.plot(range(10), [result['runtime'] for result in ga_results], label="Genetic Algorithm", color='green')
    ax.set_xlabel('Tests')
    ax.set_ylabel('Runtime')
    ax.set_title(f"Plot of Time Analysis J:{n}M:{m}")
    ax.legend()
    return fig

def visualize_schedule(algorithm_name, test_number, n, m, sequence, processing_times):
    end_times = [0] * m  
    fig, ax = plt.subplots(figsize=(10, m))
    colors = plt.get_cmap('tab20')(np.linspace(0, 1, n))
    for index in sequence:
        job_id = index % n
        machine_id = index // n
        start_time = end_times[machine_id]
        duration = processing_times[job_id][machine_id]
        ax.broken_barh([(start_time, duration)], (machine_id * 1.2 + 0.5, 0.6),
                       facecolors=colors[job_id], edgecolor='black')
        end_times[machine_id] = start_time + duration
        
        ax.text(start_time + duration / 2, machine_id * 1.2 + 0.8, f"J{job_id + 1}\n{duration}U",
                ha='center', va='center', color='white', weight='bold')

    ax.set_yticks([0.8 + 1.2 * i for i in range(m)])
    ax.set_yticklabels([f"Machine {i+1}" for i in range(m)])
    ax.set_xlabel('Time (units)')
    ax.set_title('Gantt Chart for Open Shop Scheduling')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.title(f"{algorithm_name}: test{n}{m}{test_number}" if test_number!=-1 else f"{algorithm_name}: custom test")
    plt.tight_layout()
    return fig

def read_instance(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    first_line = lines[0].split()
    n = int(first_line[0])
    m = int(first_line[1])
    processing_times = [[0]*m for _ in range(n)]
    for i in range(n):
        line = lines[i+1].split()
        for j in range(m):
            processing_times[i][j] = int(line[j])
    if len(lines) > n + 1:
        last_line = lines[-1].split()
        if len(last_line) >= 2:
            ub = int(last_line[0])
            lb = int(last_line[1])
        else:
            ub = lb = 0
    else:
        ub = lb = 0
    return n, m, processing_times, ub, lb


def read_instance_file(file):
    lines = file.readlines()
    first_line = lines[0].split()
    n = int(first_line[0])
    m = int(first_line[1])
    processing_times = [[0]*m for _ in range(n)]
    for i in range(n):
        line = lines[i+1].split()
        for j in range(m):
            processing_times[i][j] = int(line[j])
    if len(lines) > n + 1:
        last_line = lines[-1].split()
        if len(last_line) >= 2:
            ub = int(last_line[0])
            lb = int(last_line[1])
        else:
            ub = lb = 0
    else:
        ub = lb = 0
    return n, m, processing_times, ub, lb