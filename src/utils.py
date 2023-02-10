import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import tqdm
import time

######################################################
### Functions used in the notebook ###
######################################################


def load_police_data():
	''' Load data from a github repository. Data only contains 3 columns: 
        1) Complaint case reference 
        2) ID of the officer involved
        3) Total complaints on the case '''

	path_to_data = 'https://raw.githubusercontent.com/veronikasamborska1994/data_analysis_example_OWD/master/met-police-complaints.csv'
	read_pol_data = pd.read_csv(path_to_data); column_names = read_pol_data.keys()
	case_ref = read_pol_data[column_names[0]]; officer_id = read_pol_data[column_names[1]]
	complaints_per_case = read_pol_data[column_names[2]]

	return case_ref, officer_id, complaints_per_case


def inspect_data(case_ref, officer_id, complaints_per_case):
    id_unq, id_count = np.unique(officer_id, return_counts = True)
    srt_id_count = np.argsort(id_count)
    srt_cases = id_count[srt_id_count]; srt_ids = id_unq[srt_id_count]
    
    return srt_cases, srt_ids



def get_decile_data(srt_cases, srt_ids):
    'Rank officers by number of complaints and group into deciles and sum cases'
    
    id_number = np.arange(len(srt_ids));
    percentiles_id = []
    for i in np.arange(0,110,10):
        percentiles_id.append(int(np.percentile(id_number,i)))
            
    percentiles_id[-1] = percentiles_id[-1]+1        
    
    deciles_sums = []
    for i,ii in zip(percentiles_id[:-1],percentiles_id[1:]):
        deciles_sums.append((np.sum(srt_cases[i:ii])/ np.sum(srt_cases))*100)
    
    return deciles_sums


def simulate_decile_data(complaints_per_case):
    'Calulcate average probability of an offence per year per officer. Note the data we have is from the last 5 years'

    n_total_officers = 43571;  # from https://en.wikipedia.org/wiki/Metropolitan_Police
    tot_complaints = np.sum(complaints_per_case) # total number of complaints 
    unif_prob = tot_complaints/n_total_officers/5 # assume each officer has a uniform probability of a complaint (divided by 5 because the data is from the last 5 years)
   
    target_total = 0; poisson = []
    while target_total < tot_complaints or target_total == tot_complaints:
        poisson.append(np.random.poisson(unif_prob,n_total_officers))
        target_total = np.sum(poisson)    
    
        
    sum_complaints_years = np.sum(np.asarray(poisson),0)
    sim_complained_ = sum_complaints_years[np.where(sum_complaints_years!=0)[0]]
    srt_sim_id = np.argsort(sim_complained_); srt_sim_id = sim_complained_[srt_sim_id]
    
    id_number_sim = np.arange(len(sim_complained_));
    percentiles_id_sim = []
    for i in np.arange(0,110,10):
        percentiles_id_sim.append(int(np.percentile(id_number_sim,i)))
        
    deciles_sums_sim = []
    for i,ii in zip(percentiles_id_sim[:-1],percentiles_id_sim[1:]):
        deciles_sums_sim.append((np.sum(srt_sim_id[i:ii])/ np.sum(srt_sim_id))*100)
        
    return unif_prob, deciles_sums_sim
    


def calculate_poisson(lamdas, quartiles):
    n_total_officers = 43571 ; # from https://en.wikipedia.org/wiki/Metropolitan_Police
    tot_complaints = 58147; # total number of complaints in the data file 

    target_total = 0; poisson = []
    while target_total < tot_complaints or target_total == tot_complaints:
        prob_bias = []
        for l,lm in enumerate(lamdas):
            prob_bias.append(np.random.poisson(lm,int(n_total_officers/quartiles)))
        poisson.append(prob_bias)
        target_total = np.sum(np.asarray(poisson))
        
   
    poisson_sum = np.sum(poisson,0)
    sum_complaints_years = np.concatenate(poisson_sum)
    
    sim_complained_ = sum_complaints_years[np.where(sum_complaints_years!=0)[0]]
    sim_unif_prob = ((np.sum(sim_complained_))/n_total_officers/len(poisson))

    srt_sim_id = np.argsort(sim_complained_); srt_sim_id = sim_complained_[srt_sim_id]

    id_number_sim = np.arange(len(sim_complained_));
    percentiles_id_sim = []
    for i in np.arange(0,110,10):
        percentiles_id_sim.append(int(np.percentile(id_number_sim,i)))

    deciles_sums_sim = []
    for i,ii in zip(percentiles_id_sim[:-1],percentiles_id_sim[1:]):
        deciles_sums_sim.append((np.sum(srt_sim_id[i:ii])/ np.sum(srt_sim_id))*100)
    return deciles_sums_sim, len(poisson),sim_unif_prob  


def lambdas_sim(last_perc, quartiles):
    ''''((q-1)*x + last_perc))/q = unif_prob --> rearrange
    unif_prob*q = (q-1)*x + last_perc)
    ((unif_prob*q -last_perc))/(q-1) = x  '''

    unif_prob = 0.3579047794909673
    lamdas = np.zeros(quartiles);
    x = (((quartiles)*unif_prob) - last_perc)/(quartiles-1)
    lamdas[:] = x; lamdas[-1] = last_perc

    return lamdas


def lambdas_sim_graded(a,b, quartiles):
    return np.random.beta(a, b,quartiles)


def simulate_lambdas(prms):
    
    quartiles = 10; 
    permut = itertools.permutations(prms, len(prms))
    mesh = np.array(np.meshgrid(prms, prms))
    combinations = mesh.T.reshape(-1, 2)
    
    decile_responsible = []; average_complaints = []; years_to_total = []
    
    for combination in tqdm.tqdm(combinations):
        time.sleep(0.01)
        a = combination[0]; b = combination[1]
        lamdas = lambdas_sim_graded(a,b, quartiles)
        simulated, years_to, av = calculate_poisson(lamdas, quartiles)
            
        decile_responsible.append(np.round(simulated[-1],1))
        average_complaints.append(np.round(av,3))
        years_to_total.append(years_to)
        
    return decile_responsible, average_complaints, years_to_total
        
        