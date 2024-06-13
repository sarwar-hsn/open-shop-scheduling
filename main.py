import os
import time
import streamlit as st
from matplotlib import pyplot as plt
from utils import *

FOUR = 4
FIVE = 5
SEVEN = 7
from tabu_search import (
    run_tabu_search,
    run_tabu_search_tests,
)

from simulated_anneling import(
    run_simulated_anneling,
    run_simulated_anneling_tests
)

from genetic import (
    run_genetic_algorithm,
    run_genetic_algorithm_tests
)



st.markdown("<h1 style='text-align: center; color: #1da2dc;margin-bottom:50px;'>Minimal Open Shop Scheduling</h1>", unsafe_allow_html=True)
tab1,tab2,tab3,tab4 = st.tabs(tabs= ["Run Algorithms", "Compare Algorithms","Preloaded Benchmarks","Rerun Benchmarks"])

with tab1:
    selected_algorithms = st.multiselect(
        "SELECT ALGORITHMS",
        options=[TABU_SEARCH, SIMULATED_ANNEALING, GENETIC_ALGORITHM],
        default=[TABU_SEARCH, SIMULATED_ANNEALING, GENETIC_ALGORITHM]
    )

    uploaded_file = st.file_uploader(label="Choose a file")
    if uploaded_file is not None:
        n,m,processing_times,up,lb = read_instance_file(uploaded_file)
        
        for selected_algorithm in selected_algorithms:
            st.write(f"Selected Algorithm: {selected_algorithm}")
            
            if selected_algorithm == TABU_SEARCH:
                tabu_col1, tabu_col2 = st.columns(2)
                with tabu_col1:
                    tabu_iterations = st.number_input("Number of iterations", value=10000, key=f'tabu_iterations_{selected_algorithm}')   
                with tabu_col2:
                    tabu_length = st.number_input("Number of Tabu Length", value=6, key=f'tabu_length_{selected_algorithm}')   
                    
            elif selected_algorithm == SIMULATED_ANNEALING:
                sa_col1, sa_col2 = st.columns(2)
                with sa_col1:
                    sa_iterations = st.number_input("Number of iterations", value=10000, key=f'sa_iterations_{selected_algorithm}')   
            
            elif selected_algorithm == GENETIC_ALGORITHM:
                ga_col1, ga_col2, ga_col3, ga_col4 = st.columns(4)
                with ga_col1:
                    ga_iterations = st.number_input("Number of iterations", value=500, key=f'ga_iterations_{selected_algorithm}')
                with ga_col2:
                    pop_size = st.number_input("Population Size", value=200, key=f'pop_size_{selected_algorithm}')
                with ga_col3:
                    mutation_rate = st.number_input("Mutation Rate", value=0.1, key=f'mutation_rate_{selected_algorithm}') 
                with ga_col4:
                    crossover_rate = st.number_input("Crossover Rate", value=0.6, key=f'crossover_rate_{selected_algorithm}') 

        if st.button("RUN THE ALGORITHM", use_container_width=True,type="primary",key='runbtn_1'):
            for selected_algorithm in selected_algorithms:
                if selected_algorithm == TABU_SEARCH:
                    datas = run_tabu_search(n,m,processing_times,tabu_length=tabu_length, iterations=tabu_iterations)
                    fig = visualize_schedule(algorithm_name=TABU_SEARCH,test_number=-1,n=n,m=m,processing_times=datas['processing_times'],sequence=datas['sequence'])
                    st.pyplot(fig=fig)
                    st.write(f"Makespan:{datas['makespan']}")
                    st.write(f"Runtime:{datas['runtime']}")

                elif selected_algorithm == SIMULATED_ANNEALING:
                    datas = run_simulated_anneling(n,m,processing_times,ub=0,lb=0,iterations=sa_iterations)
                    fig = visualize_schedule(algorithm_name=SIMULATED_ANNEALING,test_number=-1,n=n,m=m,processing_times=datas['processing_times'],sequence=datas['sequence'])
                    st.pyplot(fig=fig)
                    st.write(f"Makespan:{datas['makespan']}")
                    st.write(f"Runtime:{datas['runtime']}")

                elif selected_algorithm == GENETIC_ALGORITHM:
                    datas = run_genetic_algorithm(n,m,processing_times,num_iters=ga_iterations,pop_size=pop_size,mutation_rate=mutation_rate)
                    fig = visualize_schedule(algorithm_name=GENETIC_ALGORITHM,test_number=-1,n=n,m=m,processing_times=datas['processing_times'],sequence=datas['sequence'])
                    st.pyplot(fig=fig)
                    st.write(f"Makespan:{datas['makespan']}")
                    st.write(f"Runtime:{datas['runtime']}")



with tab2:
    preloaded = st.checkbox("With Preloaded Results")

    if not preloaded:
        col1, col2, col3 = st.columns(3)

        with col1:
            tabu_iterations = st.number_input("Tabu Iterations", value=10000, key='tabu_iterations')
            tabu_length = st.number_input("Tabu Length", value=6, key='tabu_length')

        with col2:
            sa_iterations = st.number_input("SA Iterations", value=10000, key='sa_iterations')

        with col3:
            ga_iterations = st.number_input("GA Iterations", value=500, key='ga_iterations')
            pop_size = st.number_input("Population Size", value=200, key='pop_size')
            mutation_rate = st.number_input("Mutation Rate", value=0.1, key='mutation_rate')

    selected_test = st.selectbox("Select Test: Each Test has 10 instances", options=['4x4','5x5','7x7','15x15'], key='selection_method')

    if st.button("RUN TESTS", use_container_width=True,type="primary",key='runtestbtn'):
        
        if selected_test == '4x4':
            if not preloaded:
                run_tabu_search_tests(FOUR,FOUR,iterations=tabu_iterations)
                run_simulated_anneling_tests(FOUR,FOUR,iterations=sa_iterations)
                run_genetic_algorithm_tests(FOUR,FOUR,num_iters=ga_iterations,pop_size=pop_size,mutation_rate=mutation_rate)
                st.pyplot(fig=display_stat_makespan_single_algorithm(TABU_SEARCH,FOUR,FOUR))
                st.pyplot(fig=display_stat_makespan_single_algorithm(SIMULATED_ANNEALING,FOUR,FOUR))
                st.pyplot(fig=display_stat_makespan_single_algorithm(GENETIC_ALGORITHM,FOUR,FOUR))

                st.pyplot(fig=display_stat_runtime(FOUR,FOUR))
                st.pyplot(fig=display_stat_makespan_all_algorithm(FOUR,FOUR))
            else:
                st.pyplot(fig=display_stat_makespan_single_algorithm(TABU_SEARCH,FOUR,FOUR,load_location="predefined"))
                st.pyplot(fig=display_stat_makespan_single_algorithm(SIMULATED_ANNEALING,FOUR,FOUR,load_location="predefined"))
                st.pyplot(fig=display_stat_makespan_single_algorithm(GENETIC_ALGORITHM,FOUR,FOUR,load_location="predefined"))

                st.pyplot(fig=display_stat_runtime(FOUR,FOUR,load_location="predefined"))
                st.pyplot(fig=display_stat_makespan_all_algorithm(FOUR,FOUR,load_location="predefined"))
        
        if selected_test == '5x5':
            if not preloaded:
                run_tabu_search_tests(FIVE,FIVE,iterations=tabu_iterations)
                run_simulated_anneling_tests(FIVE,FIVE,iterations=sa_iterations)
                run_genetic_algorithm_tests(FIVE,FIVE,num_iters=ga_iterations,pop_size=pop_size,mutation_rate=mutation_rate)
                st.pyplot(fig=display_stat_makespan_single_algorithm(TABU_SEARCH,FIVE,FIVE))
                st.pyplot(fig=display_stat_makespan_single_algorithm(SIMULATED_ANNEALING,FIVE,FIVE))
                st.pyplot(fig=display_stat_makespan_single_algorithm(GENETIC_ALGORITHM,FIVE,FIVE))

                st.pyplot(fig=display_stat_runtime(FIVE,FIVE))
                st.pyplot(fig=display_stat_makespan_all_algorithm(FIVE,FIVE))
            else:
                st.pyplot(fig=display_stat_makespan_single_algorithm(TABU_SEARCH,FIVE,FIVE,load_location='predefined'))
                st.pyplot(fig=display_stat_makespan_single_algorithm(SIMULATED_ANNEALING,FIVE,FIVE,load_location='predefined'))
                st.pyplot(fig=display_stat_makespan_single_algorithm(GENETIC_ALGORITHM,FIVE,FIVE,load_location='predefined'))

                st.pyplot(fig=display_stat_runtime(FIVE,FIVE,load_location='predefined'))
                st.pyplot(fig=display_stat_makespan_all_algorithm(FIVE,FIVE,load_location='predefined'))
        
        if selected_test == '7x7':
            if not preloaded:
                run_tabu_search_tests(SEVEN,SEVEN,iterations=tabu_iterations)
                run_simulated_anneling_tests(SEVEN,SEVEN,iterations=sa_iterations)
                run_genetic_algorithm_tests(SEVEN,SEVEN,num_iters=ga_iterations,pop_size=pop_size,mutation_rate=mutation_rate)
                st.pyplot(fig=display_stat_makespan_single_algorithm(TABU_SEARCH,SEVEN,SEVEN))
                st.pyplot(fig=display_stat_makespan_single_algorithm(SIMULATED_ANNEALING,SEVEN,SEVEN))
                st.pyplot(fig=display_stat_makespan_single_algorithm(GENETIC_ALGORITHM,SEVEN,SEVEN))

                st.pyplot(fig=display_stat_runtime(SEVEN,SEVEN))
                st.pyplot(fig=display_stat_makespan_all_algorithm(SEVEN,SEVEN))
            else:
                st.pyplot(fig=display_stat_makespan_single_algorithm(TABU_SEARCH,SEVEN,SEVEN,load_location='predefined'))
                st.pyplot(fig=display_stat_makespan_single_algorithm(SIMULATED_ANNEALING,SEVEN,SEVEN,load_location='predefined'))
                st.pyplot(fig=display_stat_makespan_single_algorithm(GENETIC_ALGORITHM,SEVEN,SEVEN,load_location='predefined'))

                st.pyplot(fig=display_stat_runtime(SEVEN,SEVEN,load_location='predefined'))
                st.pyplot(fig=display_stat_makespan_all_algorithm(SEVEN,SEVEN,load_location='predefined'))

        if selected_test == '15x15':
            st.write("Are you out of your mind? Don't burn the computer please")


with tab3:
    st.pyplot(fig=display_stat_makespan_all_algorithm(FOUR,FOUR,load_location='predefined'))
    st.pyplot(fig=display_stat_makespan_all_algorithm(FIVE,FIVE,load_location='predefined'))
    st.pyplot(fig=display_stat_makespan_all_algorithm(SEVEN,SEVEN,load_location='predefined'))


    st.pyplot(fig=display_stat_runtime(FOUR,FOUR,load_location="predefined"))
    st.pyplot(fig=display_stat_runtime(FIVE,FIVE,load_location="predefined"))
    st.pyplot(fig=display_stat_runtime(SEVEN,SEVEN,load_location="predefined"))

with tab4:
    if st.button("RERUN", use_container_width=True,type="primary",key='rerun_btn'):
        run_tabu_search_tests(4,4,iterations=10000,save_location="predefined")
        run_tabu_search_tests(5,5,iterations=10000,save_location="predefined")
        run_tabu_search_tests(7,7,iterations=10000,save_location="predefined")

        run_simulated_anneling_tests(4,4,iterations=10000,save_location="predefined")
        run_simulated_anneling_tests(5,5,iterations=10000,save_location="predefined")
        run_simulated_anneling_tests(7,7,iterations=10000,save_location="predefined")

        run_genetic_algorithm_tests(4,4,num_iters=500,save_location="predefined")
        run_genetic_algorithm_tests(5,5,num_iters=500,save_location="predefined")
        run_genetic_algorithm_tests(7,7,num_iters=500,save_location="predefined")

   