"""
Study design selection logic for clinical trials.
"""
from typing import Dict, List, Optional
import logging

from models.domain import Drug, StudyDesign, PKProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StudyDesignSelector:
    """
    Service for selecting and recommending appropriate study designs.
    """
    
    def __init__(self):
        self.design_criteria = {
            "parallel": {
                "min_arms": 2,
                "allows_crossover": False,
                "typical_duration": 28,
                "advantages": ["Simple", "No carryover effects", "Suitable for long-term studies"],
                "disadvantages": ["Larger sample size", "Between-subject variability"]
            },
            "crossover": {
                "min_arms": 2,
                "allows_crossover": True,
                "typical_duration": 56,
                "advantages": ["Smaller sample size", "Within-subject comparison"],
                "disadvantages": ["Carryover effects possible", "Longer duration", "Dropout risk"]
            },
            "factorial": {
                "min_arms": 4,
                "allows_crossover": False,
                "typical_duration": 28,
                "advantages": ["Multiple interventions", "Interaction assessment"],
                "disadvantages": ["Complex analysis", "Larger sample size"]
            },
            "adaptive": {
                "min_arms": 2,
                "allows_crossover": False,
                "typical_duration": 42,
                "advantages": ["Flexible", "Efficient", "Early stopping possible"],
                "disadvantages": ["Complex design", "Regulatory challenges"]
            }
        }
    
    def recommend_design(
        self,
        drug: Drug,
        pk_profile: Optional[PKProfile] = None,
        number_of_treatments: int = 2,
        study_duration_constraint: Optional[int] = None
    ) -> StudyDesign:
        """
        Recommend an appropriate study design based on drug characteristics.
        
        Args:
            drug: Drug to be studied
            pk_profile: PK profile if available
            number_of_treatments: Number of treatment arms
            study_duration_constraint: Maximum study duration in days (optional)
        
        Returns:
            Recommended StudyDesign
        """
        logger.info(f"Recommending study design for {drug.name}")
        
        # Determine if crossover is feasible based on half-life
        crossover_feasible = True
        if pk_profile:
            half_life_param = pk_profile.get_parameter("t1/2")
            if half_life_param and half_life_param.value > 24:  # hours
                crossover_feasible = False
                logger.info("Long half-life detected - crossover not recommended")
        
        # Select design based on criteria
        if number_of_treatments == 2 and crossover_feasible:
            if study_duration_constraint and study_duration_constraint < 56:
                design_type = "parallel"
            else:
                design_type = "crossover"
        elif number_of_treatments > 2:
            design_type = "factorial" if number_of_treatments == 4 else "parallel"
        else:
            design_type = "parallel"
        
        # Create StudyDesign object
        washout_period = None
        if design_type == "crossover" and pk_profile:
            half_life_param = pk_profile.get_parameter("t1/2")
            if half_life_param:
                # Washout = 5 * half-life
                washout_period = int(5 * half_life_param.value / 24)  # Convert to days
        
        design = StudyDesign(
            design_type=design_type,
            number_of_arms=number_of_treatments,
            treatment_duration=self.design_criteria[design_type]["typical_duration"],
            washout_period=washout_period,
            blinding="double-blind",
            randomization=True
        )
        
        logger.info(f"Recommended design: {design}")
        return design
    
    def get_design_details(self, design_type: str) -> Dict:
        """
        Get detailed information about a specific design type.
        
        Args:
            design_type: Type of study design
        
        Returns:
            Dictionary with design details
        """
        if design_type not in self.design_criteria:
            raise ValueError(f"Unknown design type: {design_type}")
        
        return self.design_criteria[design_type]
    
    def compare_designs(self, design_types: List[str]) -> Dict[str, Dict]:
        """
        Compare multiple design types.
        
        Args:
            design_types: List of design types to compare
        
        Returns:
            Dictionary with comparison data
        """
        comparison = {}
        for design_type in design_types:
            if design_type in self.design_criteria:
                comparison[design_type] = self.design_criteria[design_type]
        
        return comparison
    
    def validate_design(self, design: StudyDesign) -> tuple[bool, List[str]]:
        """
        Validate a study design and return any warnings.
        
        Args:
            design: StudyDesign to validate
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        is_valid = True
        
        if design.design_type not in self.design_criteria:
            warnings.append(f"Unknown design type: {design.design_type}")
            is_valid = False
        
        criteria = self.design_criteria.get(design.design_type, {})
        min_arms = criteria.get("min_arms", 1)
        
        if design.number_of_arms < min_arms:
            warnings.append(
                f"{design.design_type} design requires at least {min_arms} arms"
            )
            is_valid = False
        
        if design.design_type == "crossover" and not design.washout_period:
            warnings.append("Crossover design should specify washout period")
        
        return is_valid, warnings


def get_design_selector() -> StudyDesignSelector:
    """
    Factory function to create a StudyDesignSelector instance.
    
    Returns:
        StudyDesignSelector instance
    """
    return StudyDesignSelector()
