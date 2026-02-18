"""
Domain entities for the oncology study management system.
Includes: Drug (препарат), PK parameters, and study design entities.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class StudyInput:
    """
    Input parameters for a bioequivalence study.
    """
    drug_name: str
    fasting: bool = True  # True = fasted (натощак), False = fed
    cv_category: str = "low"  # "low", "medium", "high"


@dataclass
class Drug:
    """
    Drug/препарат entity representing a pharmaceutical compound.
    """
    name: str
    active_ingredient: str
    indication: str
    dosage_form: str
    route_of_administration: str
    manufacturer: Optional[str] = None
    approval_status: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.name} ({self.active_ingredient})"


@dataclass
class PKParameter:
    """
    Pharmacokinetic parameter entity.
    """
    parameter_name: str  # e.g., Cmax, AUC, Tmax, t1/2, CL, Vd
    value: float
    unit: str
    coefficient_of_variation: Optional[float] = None
    source: Optional[str] = None
    population: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.parameter_name}: {self.value} {self.unit}"


@dataclass
class PKProfile:
    """
    Complete PK profile for a drug containing multiple parameters.
    """
    drug: Drug
    parameters: List[PKParameter] = field(default_factory=list)
    study_reference: Optional[str] = None
    population_characteristics: Dict[str, str] = field(default_factory=dict)
    
    def add_parameter(self, parameter: PKParameter) -> None:
        """Add a PK parameter to the profile."""
        self.parameters.append(parameter)
    
    def get_parameter(self, parameter_name: str) -> Optional[PKParameter]:
        """Get a specific PK parameter by name."""
        for param in self.parameters:
            if param.parameter_name == parameter_name:
                return param
        return None


@dataclass
class StudyDesign:
    """
    Study design entity representing the clinical trial design.
    """
    design_type: str  # parallel, crossover, factorial, adaptive
    number_of_arms: int
    treatment_duration: int  # in days
    washout_period: Optional[int] = None  # for crossover studies, in days
    blinding: str = "double-blind"  # open-label, single-blind, double-blind
    randomization: bool = True
    stratification_factors: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.design_type.capitalize()} design with {self.number_of_arms} arm(s)"


@dataclass
class StudyPopulation:
    """
    Study population entity defining inclusion/exclusion criteria.
    """
    age_range: tuple  # (min, max)
    gender: str  # male, female, all
    disease_stage: Optional[str] = None
    prior_treatment: Optional[str] = None
    exclusion_criteria: List[str] = field(default_factory=list)
    inclusion_criteria: List[str] = field(default_factory=list)


@dataclass
class Endpoint:
    """
    Study endpoint entity.
    """
    name: str
    endpoint_type: str  # primary, secondary, exploratory
    description: str
    measurement_timepoints: List[int] = field(default_factory=list)  # days
    
    def __str__(self) -> str:
        return f"{self.endpoint_type.capitalize()}: {self.name}"


@dataclass
class ClinicalStudy:
    """
    Complete clinical study entity combining all components.
    """
    study_id: str
    title: str
    drug: Drug
    pk_profile: Optional[PKProfile] = None
    design: Optional[StudyDesign] = None
    population: Optional[StudyPopulation] = None
    endpoints: List[Endpoint] = field(default_factory=list)
    sample_size: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return f"Study {self.study_id}: {self.title}"
