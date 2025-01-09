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

#Beta parameters 
alpha = 2
beta = 6

# rounds parameters
zalpha = 3.291 # 99.9% confidence



# Define the functions to plot
 
def tlap_bin_deltac_1(err, zalpha, N_values,T_percentage):
    epsilon = 0.5   # Privacy parameter
    delta = 0.00005    # Privacy parameter
    Delta_c = 1.0   # Query sensitivity
    eta_0, b, E_eta, E_eta_squared, Var_eta = truncated_laplace(epsilon, delta, Delta_c)
    rounds_list = []
    for N in N_values:
        if err == 0 : 
            err_v = 1
        else:
            err_v = err*N
        # Law of variance:
        #E[Var(X|Y=y)] = E[(N-T)*eta/(N-T)*(1-eta/(N-T))] = E[eta - eta^2/(N-T)] = E[eta] - E[eta^2]/(N-T)
        term1 = E_eta - E_eta_squared/(N-T_percentage*N) # T is a percentage of N
        # Var(E[X|Y=y]) = Var((N-T)*eta/(N-T)) = Var(eta) 
        term2 = Var_eta
        var = term1 + term2 
        rounds_denominator = err_v**2
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
        term1 = E_eta - E_eta_squared/(N-T_percentage*N)
        # Var(E[X|Y=y]) = Var((N-T)*eta/(N-T)) = Var(eta) 
        term2 = Var_eta
        var = term1 + term2 
        if err == 0 : 
            err_v = 1
        else:
            err_v = err*N
        rounds_denominator = err_v**2
        rounds_numerator = var*zalpha**2
        rounds = rounds_numerator / rounds_denominator
        rounds_list.append(np.ceil(rounds).astype(int))
    return np.array(rounds_list)

def beta_bin(alpha, beta, err, zalpha, N,T_percentage):
    rounds_list = []
    for N in N_values:
        var_denominator = (alpha+beta+1)*(alpha+beta)**2
        var_numerator = (N-T_percentage*N)*alpha*beta*(alpha+beta+N-T_percentage*N)
        var = var_numerator/var_denominator
        if err == 0 : 
            err_v = 1
        else:
            err_v = err*N
        rounds_denominator = err_v**2
        rounds_numerator = var*zalpha**2
        rounds = rounds_numerator/rounds_denominator
        rounds_list.append(np.ceil(rounds).astype(int))
    return np.array(rounds_list)


# Calculate round "r" with err being a fixed value of 1 and true result size of 0.05*N
y1 = tlap_bin_deltac_1(0, zalpha, N_values,0.05)
y2 = tlap_bin_deltac_N(0, zalpha, N_values, 0.05)
y3 = beta_bin(alpha, beta, 0, zalpha, N_values,0.05)

# Calculate round "r" with err being a percentage of N (0.01*N) and true result size of 0.05*N
f1 = tlap_bin_deltac_1(0.01, zalpha, N_values,0.05)
f2 = tlap_bin_deltac_N(0.01, zalpha, N_values, 0.05)
f3 = beta_bin(alpha, beta, 0.01, zalpha, N_values,0.05)

# Plot the functions
plt.subplot(1, 2, 1)
plt.plot(N_values, y1, c= 'orange', ls='-', marker = '*', label="Par + TLap, Δc = 1, T = 0.05N, err = 1")
plt.plot(N_values, y2 , c= 'green', ls='-', marker = '.', label="Par + TLap, Δc = sqrt(N), T = 0.05N, err = 1")
plt.plot(N_values, y3 , c= 'blue', ls=':', marker = '.', label="Par + Beta, T = 0.05N, err = 1")

plt.xscale('log')
plt.yscale('log')
# Add labels and title
plt.xlabel("Resizer Input Size N")
plt.ylabel("Rounds")

# Add a legend
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(N_values, f1, c= 'orange', ls='-', marker = '*', label="Par + TLap, Δc = 1, T = 0.05N, err = 0.01N")
plt.plot(N_values, f2, c= 'green', ls='-',marker = '.', label="Par + TLap,  Δc = sqrt(N), T = 0.05, err = 0.01N")
plt.plot(N_values, f3, c= 'blue', ls=':',marker = '.', label="Par + Beta, T = 0.05, err = 0.01N")

plt.xscale('log')
plt.yscale('log')
# Add labels and title
plt.xlabel("Resizer Input Size N")
plt.ylabel("Rounds")

# Add a legend
plt.legend()
plt.show()
