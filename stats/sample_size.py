"""
Sample size calculation for clinical trials.
"""
import math
from typing import Optional
import logging

from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleSizeCalculator:
    """
    Calculator for determining appropriate sample sizes for clinical trials.
    """
    
    def __init__(
        self,
        alpha: float = 0.05,
        power: float = 0.80,
        dropout_rate: float = 0.15
    ):
        """
        Initialize sample size calculator.
        
        Args:
            alpha: Significance level (Type I error rate)
            power: Statistical power (1 - Type II error rate)
            dropout_rate: Expected dropout rate
        """
        self.alpha = alpha
        self.power = power
        self.dropout_rate = dropout_rate
        logger.info(
            f"SampleSizeCalculator initialized: alpha={alpha}, "
            f"power={power}, dropout={dropout_rate}"
        )
    
    def calculate_parallel_design(
        self,
        effect_size: float,
        std_dev: float,
        number_of_arms: int = 2,
        allocation_ratio: float = 1.0
    ) -> dict:
        """
        Calculate sample size for parallel design.
        
        Args:
            effect_size: Expected difference between groups
            std_dev: Standard deviation
            number_of_arms: Number of treatment arms
            allocation_ratio: Ratio of allocation (e.g., 1.0 for 1:1, 2.0 for 2:1)
        
        Returns:
            Dictionary with sample size results
        """
        logger.info("Calculating sample size for parallel design")
        
        # Calculate standardized effect size (Cohen's d)
        cohens_d = effect_size / std_dev
        
        # Z-scores for alpha and power
        z_alpha = stats.norm.ppf(1 - self.alpha / 2)  # Two-tailed
        z_beta = stats.norm.ppf(self.power)
        
        # Sample size per group (for 1:1 allocation)
        n_per_group = (
            (z_alpha + z_beta) ** 2 * 2 * (std_dev ** 2) / (effect_size ** 2)
        )
        
        # Adjust for allocation ratio if not 1:1
        if allocation_ratio != 1.0:
            n_group1 = n_per_group * allocation_ratio / (1 + allocation_ratio)
            n_group2 = n_per_group / (1 + allocation_ratio)
            n_per_group = max(n_group1, n_group2)
        
        # Round up
        n_per_group = math.ceil(n_per_group)
        
        # Total sample size
        total_n = n_per_group * number_of_arms
        
        # Adjust for dropout
        adjusted_n_per_group = math.ceil(n_per_group / (1 - self.dropout_rate))
        adjusted_total_n = adjusted_n_per_group * number_of_arms
        
        result = {
            "design": "parallel",
            "n_per_group": n_per_group,
            "total_n": total_n,
            "adjusted_n_per_group": adjusted_n_per_group,
            "adjusted_total_n": adjusted_total_n,
            "effect_size": effect_size,
            "cohens_d": cohens_d,
            "alpha": self.alpha,
            "power": self.power,
            "dropout_rate": self.dropout_rate
        }
        
        logger.info(
            f"Sample size calculated: {adjusted_n_per_group} per group "
            f"(total: {adjusted_total_n})"
        )
        
        return result
    
    def calculate_crossover_design(
        self,
        effect_size: float,
        std_dev: float,
        correlation: float = 0.5
    ) -> dict:
        """
        Calculate sample size for crossover design.
        
        Args:
            effect_size: Expected difference between treatments
            std_dev: Standard deviation
            correlation: Within-subject correlation
        
        Returns:
            Dictionary with sample size results
        """
        logger.info("Calculating sample size for crossover design")
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - self.alpha / 2)
        z_beta = stats.norm.ppf(self.power)
        
        # Sample size for crossover (accounts for within-subject correlation)
        n = (
            (z_alpha + z_beta) ** 2 * 2 * (std_dev ** 2) * (1 - correlation) 
            / (effect_size ** 2)
        )
        
        n = math.ceil(n)
        
        # Adjust for dropout
        adjusted_n = math.ceil(n / (1 - self.dropout_rate))
        
        result = {
            "design": "crossover",
            "n_subjects": n,
            "adjusted_n_subjects": adjusted_n,
            "effect_size": effect_size,
            "std_dev": std_dev,
            "correlation": correlation,
            "alpha": self.alpha,
            "power": self.power,
            "dropout_rate": self.dropout_rate
        }
        
        logger.info(f"Sample size calculated: {adjusted_n} subjects")
        
        return result
    
    def calculate_bioequivalence(
        self,
        cv: float,
        bioequivalence_margin: float = 0.20,
        design: str = "crossover"
    ) -> dict:
        """
        Calculate sample size for bioequivalence study.
        
        Args:
            cv: Coefficient of variation (as decimal, e.g., 0.25 for 25%)
            bioequivalence_margin: Bioequivalence margin (default 0.20 for 80-125%)
            design: Study design ("crossover" or "parallel")
        
        Returns:
            Dictionary with sample size results
        """
        logger.info(f"Calculating sample size for bioequivalence study ({design})")
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - self.alpha)  # One-sided for TOST
        z_beta = stats.norm.ppf(self.power)
        
        # Log-transformed margin
        log_margin = math.log(1 + bioequivalence_margin)
        
        if design == "crossover":
            # Crossover design formula
            n = (
                (z_alpha + z_beta) ** 2 * 2 * (cv ** 2) / (log_margin ** 2)
            )
        else:  # parallel
            # Parallel design formula
            n = (
                (z_alpha + z_beta) ** 2 * 4 * (cv ** 2) / (log_margin ** 2)
            )
        
        n = math.ceil(n)
        adjusted_n = math.ceil(n / (1 - self.dropout_rate))
        
        result = {
            "design": design,
            "n_subjects": n if design == "crossover" else n // 2,
            "n_per_group": n // 2 if design == "parallel" else None,
            "adjusted_n_subjects": adjusted_n if design == "crossover" else adjusted_n // 2,
            "adjusted_n_per_group": adjusted_n // 2 if design == "parallel" else None,
            "cv": cv,
            "bioequivalence_margin": bioequivalence_margin,
            "alpha": self.alpha,
            "power": self.power,
            "dropout_rate": self.dropout_rate
        }
        
        logger.info(
            f"Sample size calculated: {adjusted_n if design == 'crossover' else adjusted_n // 2} "
            f"{'subjects' if design == 'crossover' else 'per group'}"
        )
        
        return result
    
    def sensitivity_analysis(
        self,
        effect_sizes: list,
        std_dev: float,
        design: str = "parallel"
    ) -> list:
        """
        Perform sensitivity analysis across multiple effect sizes.
        
        Args:
            effect_sizes: List of effect sizes to test
            std_dev: Standard deviation
            design: Study design
        
        Returns:
            List of sample size results for each effect size
        """
        logger.info("Performing sensitivity analysis")
        
        results = []
        for effect_size in effect_sizes:
            if design == "parallel":
                result = self.calculate_parallel_design(effect_size, std_dev)
            else:  # crossover
                result = self.calculate_crossover_design(effect_size, std_dev)
            results.append(result)
        
        return results


def get_sample_size_calculator(
    alpha: float = 0.05,
    power: float = 0.80,
    dropout_rate: float = 0.15
) -> SampleSizeCalculator:
    """
    Factory function to create a SampleSizeCalculator instance.
    
    Args:
        alpha: Significance level
        power: Statistical power
        dropout_rate: Expected dropout rate
    
    Returns:
        SampleSizeCalculator instance
    """
    return SampleSizeCalculator(alpha=alpha, power=power, dropout_rate=dropout_rate)
