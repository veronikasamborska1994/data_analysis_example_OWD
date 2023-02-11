import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tqdm
import time
import seaborn as sns

def default_plotting_params() -> None:
    sns.set()
    sns.set_style('white')
    params = {'legend.fontsize': 'xx-large',
            'text.usetex':False,
            'axes.labelsize': 'xx-large',
            'axes.titlesize':'xx-large',
            'xtick.labelsize':'x-large',
            'ytick.labelsize':'x-large'}
    plt.rcParams.update(params)

    
######################################################
### Functions used in the notebook ###
######################################################

def load_police_data():
	''' Load data from a github repository. Data only contains 3 columns: 
        1) Complaint case reference 
        2) ID of the officer involved
        3) Total complaints on the case '''

	path_to_data = 'https://raw.githubusercontent.com/veronikasamborska1994/data_analysis_example_OWD/master/data/met-police-complaints.csv'
	read_pol_data = pd.read_csv(path_to_data); column_names = read_pol_data.keys()
	case_ref = read_pol_data[column_names[0]]; officer_id = read_pol_data[column_names[1]]; complaints_per_case = read_pol_data[column_names[2]]
	
	return case_ref, officer_id, complaints_per_case


def inspect_data(officer_id, complaints_per_case):
    ''' Sorting officers by the number of complaints they've received.'''

    id_unq, id_count = np.unique(officer_id, return_counts = True)
    srt_id_count = np.argsort(id_count); srt_cases = id_count[srt_id_count]; srt_ids = id_unq[srt_id_count]
    
    return srt_cases, srt_ids



def get_decile_data(srt_cases, srt_ids):
    '''Group officers (ranked by the # of complaints they've received) into deciles 
       and find the proportions of complaint cases they account for.'''
    
    id_number = np.arange(len(srt_ids)); percentiles_id = []
    for i in np.arange(0,110,10):
        percentiles_id.append(int(np.percentile(id_number,i))) # get index for each percentile 
    percentiles_id[-1] = percentiles_id[-1]+1        
    
    deciles_sums = []
    for i,ii in zip(percentiles_id[:-1],percentiles_id[1:]):
        deciles_sums.append((np.sum(srt_cases[i:ii])/ np.sum(srt_cases))*100) # find a sum of complaints for each percentile
    
    return np.asarray(deciles_sums)


def simulate_decile_data(unif_prob, complaints_per_case):
    '''Simulate complaints as a possion distribution (because the officer can either receive (1) or not receive (0) a complaint).
       Note the data we have is from the last 5 years. Here let's assume that all officers have equal chance  
       of receiving a complaint (unif_prob). '''

    n_total_officers = 32493;  # from https://en.wikipedia.org/wiki/Metropolitan_Police
    tot_complaints = np.sum(complaints_per_case) # total number of complaints 
   
    target_total = 0; poisson = []
    while target_total < tot_complaints or target_total == tot_complaints: # simulate poisson distributions until we achieve a total # of complaints
        poisson.append(np.random.poisson(unif_prob,n_total_officers))
        target_total = np.sum(poisson)  # sum complaints to check when the total of complains has been achieved
    
        
    sim_complained_ = sum_complaints_years[np.where(target_total!=0)[0]] # find which officers had a complaint
    srt_sim_id = np.argsort(sim_complained_); srt_sim_id = sim_complained_[srt_sim_id] # sort officer by total # of complaints
    
    id_number_sim = np.arange(len(sim_complained_));
    percentiles_id_sim = []
    for i in np.arange(0,110,10): # get index for each percentile 
        percentiles_id_sim.append(int(np.percentile(id_number_sim,i)))
        
    deciles_sums_sim = []
    for i,ii in zip(percentiles_id_sim[:-1],percentiles_id_sim[1:]):
        deciles_sums_sim.append((np.sum(srt_sim_id[i:ii])/ np.sum(srt_sim_id))*100) # find a sum of complaints for each percentile
        
    return unif_prob, np.asarray(deciles_sums_sim)
    


def simulate_non_uniform(lamdas, quartiles):
    ''' '''

    n_total_officers = 32493 ; # from https://en.wikipedia.org/wiki/Metropolitan_Police
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

    return np.asarray(deciles_sums_sim), len(poisson), sim_unif_prob  



def lambdas_sim_graded(a,b, quartiles):
    return np.random.beta(a, b,quartiles)


def sort_lambdas(lamdas):
    srtd_lambdas = np.sort(lamdas)
    id_number = np.arange(len(lamdas));
    percentiles_id = []
    for i in np.arange(0,110,10):
        percentiles_id.append(int(np.percentile(id_number,i)))
            
    percentiles_id[-1] = percentiles_id[-1]+1        
    
    deciles_sums = []
    for i,ii in zip(percentiles_id[:-1],percentiles_id[1:]):
        deciles_sums.append(np.mean(srtd_lambdas[i:ii]))
    return np.asarray(deciles_sums)
   
    

def simulate_lambdas(prms):
    n_total_officers = 32493; 
    quartiles = int(n_total_officers/100) # divide total # of officers into a 100 quartiles to reduce code running time 
    mesh = np.array(np.meshgrid(prms, prms)) # get permutations of different a and b values for the gamma distribution
    combinations = mesh.T.reshape(-1, 2) 
    
    decile_responsible = []; average_complaints = []; years_to_total = []; labmdas_dec = [] 
    for combination in tqdm.tqdm(combinations):
        time.sleep(0.01)
        a = combination[0]; b = combination[1]
        lamdas = lambdas_sim_graded(a,b, quartiles)
        simulated, years_to, av = simulate_non_uniform(lamdas, quartiles)
        yearly_prob = sort_lambdas(lamdas)
  
        decile_responsible.append(np.round(simulated[-1],1))
        average_complaints.append(np.round(av,3))
        years_to_total.append(years_to)
        labmdas_dec.append(yearly_prob)
        
    return np.asarray(decile_responsible), np.asarray(average_complaints), np.asarray(years_to_total), np.asarray(labmdas_dec)
        
        