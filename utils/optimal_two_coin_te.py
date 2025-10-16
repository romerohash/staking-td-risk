import numpy as np
from math import sqrt


def make_cov(asset_sigmas, rho_I, rho_E, rho_cross):
    cov = np.diag(asset_sigmas**2)
    cov[0, 1] = cov[1, 0] = rho_I * asset_sigmas[0] * asset_sigmas[1]
    for i in range(2, 6):
        for j in range(i + 1, 6):
            cov[i, j] = cov[j, i] = rho_E * asset_sigmas[i] * asset_sigmas[j]
    for i in (0, 1):  # BTC & ETH
        for j in range(2, 6):  # the four other coins
            cov[i, j] = cov[j, i] = rho_cross * asset_sigmas[i] * asset_sigmas[j]
    return cov


def optimal_two_coin_weights(bench, sigmas, rho_I, rho_E, rho_cross):
    """Return (btc_weight, eth_weight) that minimises TE."""
    cov = make_cov(sigmas, rho_I, rho_E, rho_cross)
    delta_w0 = np.array([
        -bench[0],
        1 - bench[1],
        -bench[2],
        -bench[3],
        -bench[4],
        -bench[5],
    ])
    s = np.array([1, -1, 0, 0, 0, 0])
    x_star = -(s @ cov @ delta_w0) / (s @ cov @ s)  # unconstrained optimum
    x_star = max(0.0, min(1.0, x_star))  # project to [0,1]
    return x_star, 1 - x_star


def tracking_error(active_w, cov):
    return sqrt(active_w @ cov @ active_w)


# --- example (expected scenario) -------------------------------------------
bench = np.array([0.7869, 0.1049, 0.0549, 0.0387, 0.0119, 0.0027])
sig = np.array([3.9, 4.8, 5.3, 7.1, 5.5, 5.1]) / 100

btc_w, eth_w = optimal_two_coin_weights(
    bench,
    sig,
    rho_I=0.70,
    rho_E=0.60,
    rho_cross=0.60,
)

cov = make_cov(sig, 0.70, 0.60, 0.60)
corr = cov / np.outer(sig, sig)
te_daily = tracking_error(np.array([btc_w, eth_w, 0, 0, 0, 0]) - bench, cov)
te_annual = te_daily * sqrt(252)

print(f'Optimal weights  : BTC {btc_w:.4%} | ETH {eth_w:.4%}')
print(f'Tracking error   : {te_daily:.4%} daily ≈ {te_annual:.2%} annual')
