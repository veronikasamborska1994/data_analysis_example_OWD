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
    '''
    Load data from a GitHub repository containing two columns: 
    1) Complaint case reference 
    2) ID of the officer involved

    Returns:
    case_ref: numpy array 
        An array of complaint case references
    officer_id: numpy array
        An array of officer IDs
    '''
   
    path_to_data = 'https://raw.githubusercontent.com/veronikasamborska1994/data_analysis_example_OWD/master/data/met-police-complaints.csv'
    read_pol_data = pd.read_csv(path_to_data); column_names = read_pol_data.keys()
    case_ref = read_pol_data[column_names[0]]; officer_id = read_pol_data[column_names[1]]
    
    return np.asarray(case_ref), np.asarray(officer_id)


def inspect_data(officer_id: np.ndarray):
    '''
    Sort the given `officer_id` array by the number of complaints each officer has received.
    
    Args:
    officer_id: numpy array
        A 1D numpy array of integers representing officer IDs.
    
    Returns:
    srt_cases: numpy array
        A 1D numpy array of integers representing the number of complaints each officer has received, sorted in ascending order.
    srt_ids: numpy array
        A 1D numpy array of integers representing officer IDs, sorted in ascending order of the number of complaints they have received.
    '''
    id_unq, id_count = np.unique(officer_id, return_counts = True)
    srt_id_count = np.argsort(id_count); srt_cases = id_count[srt_id_count]; srt_ids = id_unq[srt_id_count]
    
    return srt_cases, srt_ids



def get_decile_data(srt_cases: np.ndarray, srt_ids: np.ndarray):
    """
    Computes the proportion of complaint cases accounted for by each decile of officers, where officers are ranked 
    by the number of complaints they have received.

    Args:
    srt_cases: numpy array
        Array of integers representing the number of complaints each officer has received, 
        sorted in descending order.
    srt_ids: numpy array
        Array of integers representing the IDs of each officer, sorted in descending order 
        according to the number of complaints.

    Returns:
    deciles_sums: numpy array
        An array of floats representing the proportion of complaint cases accounted for by each decile of officers.
    """
    
    id_number = np.arange(len(srt_ids)); percentiles_id = []
    for i in np.arange(0,110,10):
        percentiles_id.append(int(np.percentile(id_number,i))) # get index for each percentile 
    percentiles_id[-1] = percentiles_id[-1]+1        
    
    deciles_sums = []
    for i,ii in zip(percentiles_id[:-1],percentiles_id[1:]):
        deciles_sums.append((np.sum(srt_cases[i:ii])/ np.sum(srt_cases))*100) # find a sum of complaints for each percentile
    
    return np.asarray(deciles_sums)


def simulate_decile_data(unif_prob: float, tot_complaints: int, n_total_officers: int):
    """
    Simulates the distribution of complaints across officers for a given uniform probability distribution, using Poisson simulation.

    Parameters:
    -----------
    unif_prob : float
        The probability of an officer receiving a complaint in a given year.
    tot_complaints : int
        The total number of complaints to be generated in the simulation.
    n_total_officers : int
        The total number of officers in the simulation.

    Returns:
    --------
    deciles_sums_sim : numpy array
        An array of the sum of complaints for each decile (10th percentile range) of officers in the simulation (np.ndarray).
    
    """
    target_total = 0; poisson = [] 
    while target_total < tot_complaints or target_total == tot_complaints: # simulate poisson distributions until we achieve a total # of complaints
        poisson.append(np.random.poisson(unif_prob,n_total_officers)) # draw samples from a possion distribution
        target_total = np.sum(poisson)  # sum complaints to check when the total of complains has been achieved
    
    sim_complained_total = np.sum(np.asarray(poisson),0) # sum over years
    sim_complained_ = sim_complained_total[np.where(sim_complained_total!=0)[0]] # find which officers had a complaint
    srt_sim_id = np.argsort(sim_complained_); srt_sim_id = sim_complained_[srt_sim_id] # sort officer by total # of complaints
    
    id_number_sim = np.arange(len(sim_complained_)); percentiles_id_sim = []
    
    for i in np.arange(0,110,10): # get index for each percentile 
        percentiles_id_sim.append(int(np.percentile(id_number_sim,i)))
        
    deciles_sums_sim = []
    for i,ii in zip(percentiles_id_sim[:-1],percentiles_id_sim[1:]): # loop through each percentile indicies
        deciles_sums_sim.append((np.sum(srt_sim_id[i:ii])/ np.sum(srt_sim_id))*100) # find a sum of complaints for each percentile
        
    return unif_prob, np.asarray(deciles_sums_sim)
    


def simulate_non_uniform(lamdas: list, quartiles: int, tot_complaints: int, n_total_officers: int):
    """
    This function simulates non-uniform complaints for a given list of yearly probability values, "lamdas",
    using a Poisson distribution to generate the number of complaints per officer per year. The simulation
    continues until the total number of simulated complaints equals or exceeds the input value "tot_complaints".
    The function returns the decile sums of the simulated complaints, the number of years it took to reach the
    total number of simulated complaints, and the average probability of a complaint per officer per year.

    Parameters:
    -----------
    lamdas : list
        A list of yearly probability values for generating complaints using a Poisson distribution.
    quartiles : int
        The number of quartiles to use in the simulation.
    tot_complaints : int
        The total number of complaints to simulate.
    n_total_officers : int
        The total number of officers in the simulation.

    Returns:
    --------
    deciles_sums_sim : numpy array
        An array of the decile sums of the simulated complaints.
    years_to_total : int
        The number of years it took to reach the total number of simulated complaints.
    sim_av_prob : float
        The average probability of a complaint per officer per year.
    """

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
    sim_av_prob = ((np.sum(sim_complained_))/n_total_officers/len(poisson))
    years_to_total = len(poisson)

    srt_sim_id = np.argsort(sim_complained_); srt_sim_id = sim_complained_[srt_sim_id]

    id_number_sim = np.arange(len(sim_complained_));
    percentiles_id_sim = []
    for i in np.arange(0,110,10):
        percentiles_id_sim.append(int(np.percentile(id_number_sim,i)))

    deciles_sums_sim = []
    for i,ii in zip(percentiles_id_sim[:-1],percentiles_id_sim[1:]):
        deciles_sums_sim.append((np.sum(srt_sim_id[i:ii])/ np.sum(srt_sim_id))*100)

    return np.asarray(deciles_sums_sim), years_to_total, sim_av_prob  



def beta_distr(a: float, b: float, quartiles: int): 
    """
    This function generates a random beta distribution using the input parameters "a" and "b", with a length 
    specified by "quartiles". The function returns an array of the randomly generated values.

    Parameters:
    -----------
    a : float
        The shape parameter for the beta distribution.
    b : float
        The scale parameter for the beta distribution.
    quartiles : int
        The length of the array to be returned.

    Returns:
    --------
    beta_values : numpy array
        An array of the randomly generated values from the beta distribution with shape parameter "a" and 
        scale parameter "b", with a length specified by "quartiles".
    """
   
    return np.random.beta(a, b, quartiles)

    
def simulate_lambdas(prms: np.ndarray, quartiles: int, tot_complaints: int, n_total_officers: int):
    """
    Given a set of input parameters, this function generates permutations of different "a" and "b" values for a 
    beta distribution. It then uses these values to compute decile probabilities of responsibility for a given 
    complaint, simulate the number of complaints each officer receives, compute the average number of complaints 
    per officer, and determine the number of years it would take for all officers to receive a total number of 
    complaints equal to "tot_complaints". The function returns arrays of the final decile probabilities of 
    responsibility, the average number of complaints per officer, the number of years it would take to reach the 
    total number of complaints, and the decile probabilities for each simulation.

    Parameters:
    -----------
    prms : numpy array
        An array of "a" and "b" values for the beta distribution to be simulated.
    quartiles : numpy array
        An array of quartile values for the distribution of complaints among officers.
    tot_complaints : int
        The total number of complaints to be distributed among officers.
    n_total_officers : int
        The total number of officers in the simulation.

    Returns:
    --------
    decile_responsible : numpy array
        An array of the final decile probabilities of responsibility for a given complaint.
    average_complaints : numpy array
        An array of the average number of complaints per officer for each simulation.
    years_to_total : numpy array
        An array of the number of years it would take for all officers to receive a total number of complaints 
        equal to "tot_complaints" for each simulation.
    labmdas_dec : numpy array
        An array of the decile probabilities of responsibility for each simulation.
    """

    mesh = np.array(np.meshgrid(prms, prms)) # get permutations of different a and b values for the beta distribution
    combinations = mesh.T.reshape(-1, 2) 
    
    decile_responsible = []; average_complaints = []; years_to_total = []; labmdas_dec = [] 
    for combination in tqdm.tqdm(combinations):
        time.sleep(0.01)
        a = combination[0]; b = combination[1]
        lamdas = beta_distr(a,b, quartiles)
        simulated, years_to, av = simulate_non_uniform(lamdas, quartiles, tot_complaints,n_total_officers)
        yearly_prob = sort_lambdas(lamdas)
  
        decile_responsible.append(np.round(simulated[-1],1))
        average_complaints.append(np.round(av,3))
        years_to_total.append(years_to)
        labmdas_dec.append(yearly_prob)
        
    return np.asarray(decile_responsible), np.asarray(average_complaints), np.asarray(years_to_total), np.asarray(labmdas_dec)


def sort_lambdas(lamdas: np.ndarray):
    """
    Given an input array of lambdas, this function sorts the array in ascending order, computes the mean value 
    for each of ten deciles, and returns an array of these mean values.

    Parameters:
    -----------
    lamdas : numpy array
        An array of lambdas to be sorted and grouped into deciles.
        
    Returns:
    --------
    deciles_sums : numpy array
        An array of ten mean values, where each mean value represents the average lambda value within one of ten 
        equally-sized deciles of the sorted input array.
    """

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
     
        