import numpy as np
from scipy.integrate import quad
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv

def truncated_laplace(epsilon, delta, Delta_c):
    """
    Computes eta^0, b, E(eta), E(eta^2), and Var(eta) for the Laplace mechanism with infinite range.

    Parameters:
        epsilon: Privacy parameter epsilon
        delta: Privacy parameter delta
        Delta_c: Query sensitivity

    Returns:
        eta_0: Truncation adjustment value
        b: Scale parameter of the Laplace distribution
        E_eta: Expected value of eta
        E_eta_squared: Expected value of eta^2
        Var_eta: Variance of eta
    """
    # Scale parameter of the Laplace distribution
    b = Delta_c / epsilon

    # Compute eta^0 for the infinite range
    eta_0 = -b * np.log((np.exp(epsilon /Delta_c) + 1) * delta) + Delta_c
    

    # Compute E(eta), E(eta^2), and Var(eta) for the infinite range
    E_eta = eta_0
    E_eta_squared = eta_0**2 + 2 * b**2
    Var_eta = 2 * b**2

    return eta_0, b, E_eta, E_eta_squared, Var_eta    
# Generate N values (relation size)
N_values = np.linspace(100, 1000000, 50, dtype=int)


# rounds parameters
zalpha = 3.291 # 99.9% confidence



# Define the functions to plot
def seq_tlap_deltac_1(err, zalpha):
    epsilon = 0.5   # Privacy parameter
    delta = 0.00005    # Privacy parameter
    Delta_c = 1.0   # Query sensitivity
    eta_0, b, E_eta, E_eta_squared, Var_eta = truncated_laplace(epsilon, delta, Delta_c)
    rounds_denominator = err**2
    rounds_numerator = Var_eta*zalpha**2
    rounds = rounds_numerator / rounds_denominator
    return np.ceil(rounds).astype(int)

def seq_tlap_deltac_N(err, zalpha, N_values):
    epsilon = 0.5   # Privacy parameter
    delta = 0.00005    # Privacy parameter
    rounds_list = []
    for N in N_values:
        Delta_c = np.sqrt(N)  # Query sensitivity
        eta_0, b, E_eta, E_eta_squared, Var_eta = truncated_laplace(epsilon, delta, Delta_c)
        rounds_denominator = err**2
        rounds_numerator = Var_eta*zalpha**2
        rounds = rounds_numerator / rounds_denominator
        rounds_list.append(np.ceil(rounds).astype(int))
    return np.array(rounds_list)

 
def tlap_bin_deltac_1(err, zalpha, N_values,T_percentage):
    epsilon = 0.5   # Privacy parameter
    delta = 0.00005    # Privacy parameter
    Delta_c = 1.0   # Query sensitivity
    eta_0, b, E_eta, E_eta_squared, Var_eta = truncated_laplace(epsilon, delta, Delta_c)
    rounds_list = []
    for N in N_values:
        # Law of variance:
        #E[Var(X|Y=y)] = E[(N-T)*eta/(N-T)*(1-eta/(N-T))] = E[eta - eta^2/(N-T)] = E[eta] - E[eta^2]/(N-T)
        term1 = E_eta - E_eta_squared/(N-T_percentage*N) # T is a percentage of N
        # Var(E[X|Y=y]) = Var((N-T)*eta/(N-T)) = Var(eta) 
        term2 = Var_eta
        var = term1 + term2 
        rounds_denominator = err**2
        rounds_numerator = var*zalpha**2
        rounds = rounds_numerator / rounds_denominator
        rounds_list.append(np.ceil(rounds).astype(int))
    return np.array(rounds_list)
    
def tlap_bin_deltac_N(err, zalpha, N_values,T_percentage):
    epsilon = 0.5   # Privacy parameter
    delta = 0.00005    # Privacy parameter   
    rounds_list = []
    for N in N_values:
        Delta_c = np.sqrt(N)   # Query sensitivity
        eta_0, b, E_eta, E_eta_squared, Var_eta = truncated_laplace(epsilon, delta, Delta_c)
        # Law of variance:
        #E[Var(X|Y=y)] = E[(N-T)*eta/(N-T)*(1-eta/(N-T))] = E[eta - eta^2/(N-T)] = E[eta] - E[eta^2]/(N-T)
        term1 = E_eta - E_eta_squared/(N-T_percentage*N) # T is a percentage of N
        # Var(E[X|Y=y]) = Var((N-T)*eta/(N-T)) = Var(eta) 
        term2 = Var_eta
        var = term1 + term2 
        rounds_denominator = err**2
        rounds_numerator = var*zalpha**2
        rounds = rounds_numerator / rounds_denominator
        rounds_list.append(np.ceil(rounds).astype(int))
    return np.array(rounds_list)

#Calculate round "r" with err being a fixed value of 1 and true result size of 0.1*N and 0.5*N
y1 = seq_tlap_deltac_N(1, zalpha, N_values)
y2 = tlap_bin_deltac_N(1, zalpha, N_values, 0.1)
y3 = tlap_bin_deltac_N(1, zalpha, N_values, 0.5)

f1 = np.full_like(N_values, seq_tlap_deltac_1(1, zalpha))
f2 = tlap_bin_deltac_1(1, zalpha, N_values,0.1)
f3 = tlap_bin_deltac_1(1, zalpha, N_values,0.5)

# Plot the functions

plt.subplot(1, 2, 1)
plt.plot(N_values, f1, c= 'orange', ls=':', marker = '*', label="Seq + TLap, Δc = 1")
plt.plot(N_values, f2 , c= 'green', ls='-', marker = '.', label="Par + TLap, Δc = 1, T = 0.1N")
plt.plot(N_values, f3 , c= 'blue', ls='-', marker = '.', label="Par + TLap, Δc = 1, T = 0.5N")

plt.xscale('log')
plt.yscale('log')
# Add labels
plt.xlabel("Resizer Input Size N")
plt.ylabel("Rounds")

# Add a legend
plt.legend()


plt.subplot(1, 2, 2)
plt.plot(N_values, y1, c= 'orange', ls=':', marker = '*', label="Seq + TLap, Δc = sqrt(N)")
plt.plot(N_values, y2, c= 'green', ls='-',marker = '.', label="Par + TLap,  Δc = sqrt(N), T = 0.1N")
plt.plot(N_values, y3, c= 'blue', ls='-',marker = '.', label="Par + TLap,  Δc = sqrt(N), T = 0.5N")

plt.xscale('log')
plt.yscale('log')
# Add labels
plt.xlabel("Resizer Input Size N")
plt.ylabel("Rounds")

# Add a legend
plt.legend()

# Show the plot
plt.show()
