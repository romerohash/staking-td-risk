"""
Analytical Variance Model for Stochastic Redemption Framework
============================================================

Implements the mathematically correct relationship between variance 
and redemption percentage, accounting for the non-constant k_factor.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from math import sqrt
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class VarianceModel:
    """
    Analytical model for tracking error variance as a function of redemption.
    
    Key insight: variance is NOT proportional to redemption_pct², but rather
    to (redemption_pct - threshold)² where threshold = (1 - staking_pct).
    """
    eth_weight: float
    staking_pct: float
    base_k: float  # k = eth_weight² × (v' Σ v) from optimization
    
    @property
    def redemption_threshold(self) -> float:
        """Redemption level below which no ETH overweight is needed"""
        return 1 - self.staking_pct
    
    def delta_eth(self, redemption_pct: float) -> float:
        """ETH overweight required for given redemption"""
        if redemption_pct <= self.redemption_threshold:
            return 0.0
        return self.eth_weight * (redemption_pct - self.redemption_threshold)
    
    def variance(self, redemption_pct: float) -> float:
        """
        Daily variance as a function of redemption percentage.
        
        Derivation:
        1. delta_eth = eth_weight × max(0, redemption_pct - (1 - staking_pct))
        2. active_weights = delta_eth × v (where v is fixed optimization vector)
        3. variance = active' × Σ × active = delta_eth² × (v' Σ v)
        
        Therefore:
        variance = eth_weight² × (redemption_pct - threshold)² × (v' Σ v)
                 = base_k × (redemption_pct - threshold)²
        """
        if redemption_pct <= self.redemption_threshold:
            return 0.0
        return self.base_k * (redemption_pct - self.redemption_threshold)**2
    
    def effective_k_factor(self, redemption_pct: float) -> float:
        """
        The 'k_factor' if we were to express variance = k_factor × redemption_pct².
        
        Shows why k_factor cannot be constant: it depends on redemption_pct!
        """
        if redemption_pct <= self.redemption_threshold or redemption_pct == 0:
            return 0.0
        return self.variance(redemption_pct) / redemption_pct**2
    
    def tracking_error(self, redemption_pct: float, duration_days: int) -> float:
        """Annual tracking error for a single redemption episode"""
        daily_var = self.variance(redemption_pct)
        return sqrt(daily_var * duration_days)


class StochasticVarianceModel:
    """
    Extended model for stochastic redemptions with correct variance calculation.
    """
    
    def __init__(self, variance_model: VarianceModel):
        self.vm = variance_model
    
    def expected_variance_contribution(self, mean_r: float, var_r: float) -> float:
        """
        E[variance(R)] where R is a random redemption size.
        
        For R > threshold, variance = base_k × (R - threshold)²
        
        This requires the second moment of the truncated distribution.
        """
        threshold = self.vm.redemption_threshold
        
        if mean_r <= threshold:
            # Most redemptions below threshold
            return 0.0
        
        # For simplicity, assume all redemptions > threshold
        # E[(R - threshold)²] = Var[R] + (E[R] - threshold)²
        return self.vm.base_k * (var_r + (mean_r - threshold)**2)
    
    def analytical_tracking_error(self, lambda_redemptions: float,
                                 mean_r: float, var_r: float,
                                 duration_days: int) -> float:
        """
        Analytical TE with correct variance model.
        
        TE = √(Σ variance_i × days_i)
        
        For stochastic model:
        TE = √(λ × E[variance(R)] × days)
        """
        expected_var = self.expected_variance_contribution(mean_r, var_r)
        total_var_days = lambda_redemptions * expected_var * duration_days
        return sqrt(total_var_days)


def demonstrate_k_factor_variation():
    """Show how k_factor varies with redemption percentage"""
    # Example parameters
    model = VarianceModel(
        eth_weight=0.1049,
        staking_pct=0.8,
        base_k=0.001  # Placeholder - would be calculated from covariance
    )
    
    print("K-FACTOR VARIATION WITH REDEMPTION SIZE")
    print("=" * 60)
    print(f"Threshold: {model.redemption_threshold:.1%} (below this, k_factor = 0)")
    print("\nRedemption   Delta_ETH   Variance    k_factor    Ratio to k")
    print("-" * 60)
    
    redemptions = [0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00]
    k_at_100 = model.effective_k_factor(1.0)
    
    for r in redemptions:
        delta = model.delta_eth(r)
        var = model.variance(r)
        k_eff = model.effective_k_factor(r)
        ratio = k_eff / model.base_k if model.base_k > 0 else 0
        
        print(f"{r:6.1%}      {delta:8.4f}   {var:8.6f}   {k_eff:8.6f}   {ratio:6.3f}")
    
    print("\nKey insight: k_factor approaches base_k × staking_pct² as r → 1")
    print(f"Limiting value: {model.base_k * model.staking_pct**2:.6f}")


def corrected_stochastic_example():
    """Example using the corrected variance model"""
    # Market parameters
    vm = VarianceModel(
        eth_weight=0.1049,
        staking_pct=0.8,
        base_k=0.001
    )
    
    # Stochastic model
    stoch = StochasticVarianceModel(vm)
    
    # Example: 20 redemptions averaging 30% with std 10%
    te = stoch.analytical_tracking_error(
        lambda_redemptions=20,
        mean_r=0.30,
        var_r=0.01,  # std = 0.1, var = 0.01
        duration_days=10
    )
    
    print("\n\nCORRECTED STOCHASTIC MODEL")
    print("=" * 60)
    print(f"Expected redemptions: 20")
    print(f"Mean redemption size: 30%")
    print(f"Redemption std dev: 10%")
    print(f"Duration: 10 days")
    print(f"Analytical TE: {te:.4%}")
    
    # Compare with naive constant k approach
    naive_k = 0.001  # Assuming variance = k × r²
    naive_te = sqrt(naive_k * 20 * (0.09 + 0.01) * 10)
    print(f"\nNaive approach (constant k): {naive_te:.4%}")
    print(f"Error from naive approach: {(naive_te/te - 1)*100:+.1f}%")


if __name__ == "__main__":
    demonstrate_k_factor_variation()
    corrected_stochastic_example()