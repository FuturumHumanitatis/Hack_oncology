"""
Templates for generating text blocks in the study synopsis.
"""
from typing import Dict, Optional
from models.domain import ClinicalStudy, Drug, StudyDesign, StudyPopulation, Endpoint


class SynopsisTemplates:
    """
    Templates for various sections of a clinical trial synopsis.
    """
    
    @staticmethod
    def title_section(study: ClinicalStudy) -> str:
        """Generate title section."""
        return f"""
STUDY SYNOPSIS

Protocol Number: {study.study_id}
Title: {study.title}
Drug: {study.drug.name} ({study.drug.active_ingredient})
Indication: {study.drug.indication}

Date: {study.created_at.strftime('%Y-%m-%d')}
"""
    
    @staticmethod
    def background_section(drug: Drug) -> str:
        """Generate background section."""
        return f"""
BACKGROUND AND RATIONALE

{drug.name} is a {drug.dosage_form} formulation containing {drug.active_ingredient} 
for the treatment of {drug.indication}. The drug is administered via {drug.route_of_administration}.

This study aims to evaluate the pharmacokinetic properties and safety profile of {drug.name} 
in the target patient population.
"""
    
    @staticmethod
    def objectives_section(endpoints: list) -> str:
        """Generate objectives section."""
        primary_endpoints = [e for e in endpoints if e.endpoint_type == "primary"]
        secondary_endpoints = [e for e in endpoints if e.endpoint_type == "secondary"]
        
        text = "STUDY OBJECTIVES\n\n"
        
        if primary_endpoints:
            text += "Primary Objectives:\n"
            for i, endpoint in enumerate(primary_endpoints, 1):
                text += f"{i}. {endpoint.name}: {endpoint.description}\n"
            text += "\n"
        
        if secondary_endpoints:
            text += "Secondary Objectives:\n"
            for i, endpoint in enumerate(secondary_endpoints, 1):
                text += f"{i}. {endpoint.name}: {endpoint.description}\n"
        
        return text
    
    @staticmethod
    def study_design_section(design: StudyDesign) -> str:
        """Generate study design section."""
        text = f"""
STUDY DESIGN

Design Type: {design.design_type.capitalize()}
Number of Arms: {design.number_of_arms}
Treatment Duration: {design.treatment_duration} days
Blinding: {design.blinding.capitalize()}
Randomization: {'Yes' if design.randomization else 'No'}
"""
        
        if design.washout_period:
            text += f"Washout Period: {design.washout_period} days\n"
        
        if design.stratification_factors:
            text += f"Stratification Factors: {', '.join(design.stratification_factors)}\n"
        
        return text
    
    @staticmethod
    def study_population_section(population: Optional[StudyPopulation]) -> str:
        """Generate study population section."""
        if not population:
            return """
STUDY POPULATION

To be determined based on study requirements.
"""
        
        text = f"""
STUDY POPULATION

Age Range: {population.age_range[0]}-{population.age_range[1]} years
Gender: {population.gender.capitalize()}
"""
        
        if population.disease_stage:
            text += f"Disease Stage: {population.disease_stage}\n"
        
        if population.prior_treatment:
            text += f"Prior Treatment: {population.prior_treatment}\n"
        
        if population.inclusion_criteria:
            text += "\nInclusion Criteria:\n"
            for i, criterion in enumerate(population.inclusion_criteria, 1):
                text += f"{i}. {criterion}\n"
        
        if population.exclusion_criteria:
            text += "\nExclusion Criteria:\n"
            for i, criterion in enumerate(population.exclusion_criteria, 1):
                text += f"{i}. {criterion}\n"
        
        return text
    
    @staticmethod
    def treatment_section(drug: Drug, design: StudyDesign) -> str:
        """Generate treatment section."""
        return f"""
TREATMENT

Investigational Product: {drug.name}
Active Ingredient: {drug.active_ingredient}
Dosage Form: {drug.dosage_form}
Route of Administration: {drug.route_of_administration}

Treatment Duration: {design.treatment_duration} days
Number of Treatment Arms: {design.number_of_arms}
"""
    
    @staticmethod
    def endpoints_section(endpoints: list) -> str:
        """Generate endpoints section."""
        text = "STUDY ENDPOINTS\n\n"
        
        for endpoint in endpoints:
            text += f"{endpoint.endpoint_type.capitalize()} Endpoint: {endpoint.name}\n"
            text += f"Description: {endpoint.description}\n"
            if endpoint.measurement_timepoints:
                timepoints_str = ", ".join([f"Day {t}" for t in endpoint.measurement_timepoints])
                text += f"Assessment Timepoints: {timepoints_str}\n"
            text += "\n"
        
        return text
    
    @staticmethod
    def statistical_analysis_section(design: StudyDesign, sample_size: Optional[int]) -> str:
        """Generate statistical analysis section."""
        text = """
STATISTICAL ANALYSIS

Analysis Population:
- Intent-to-Treat (ITT) population
- Per-Protocol (PP) population
- Safety population

Primary Analysis:
Statistical tests will be performed at a significance level of α = 0.05 (two-sided).
"""
        
        if design.design_type == "parallel":
            text += "\nFor parallel design, between-group comparisons will be performed using appropriate statistical tests (t-test, ANOVA, etc.).\n"
        elif design.design_type == "crossover":
            text += "\nFor crossover design, within-subject comparisons will be performed accounting for period and sequence effects.\n"
        
        return text
    
    @staticmethod
    def sample_size_section(sample_size_result: Dict) -> str:
        """Generate sample size section."""
        design = sample_size_result.get("design", "unknown")
        
        text = "SAMPLE SIZE CALCULATION\n\n"
        
        if design == "parallel":
            text += f"Design: Parallel\n"
            text += f"Sample Size per Group: {sample_size_result.get('adjusted_n_per_group', 'N/A')}\n"
            text += f"Total Sample Size: {sample_size_result.get('adjusted_total_n', 'N/A')}\n"
        elif design == "crossover":
            text += f"Design: Crossover\n"
            text += f"Total Subjects: {sample_size_result.get('adjusted_n_subjects', 'N/A')}\n"
        
        text += f"\nStatistical Parameters:\n"
        text += f"- Significance Level (α): {sample_size_result.get('alpha', 0.05)}\n"
        text += f"- Power (1-β): {sample_size_result.get('power', 0.80)}\n"
        text += f"- Expected Dropout Rate: {sample_size_result.get('dropout_rate', 0.15) * 100:.0f}%\n"
        
        if "effect_size" in sample_size_result:
            text += f"- Expected Effect Size: {sample_size_result['effect_size']}\n"
        
        return text
    
    @staticmethod
    def regulatory_section(regulatory_body: str = "FDA") -> str:
        """Generate regulatory section."""
        return f"""
REGULATORY CONSIDERATIONS

This study will be conducted in accordance with:
- Good Clinical Practice (GCP) guidelines
- Declaration of Helsinki
- {regulatory_body} regulations and guidance
- Local regulatory requirements

Ethics:
- Ethics Committee/IRB approval will be obtained before study initiation
- Written informed consent will be obtained from all participants

Registration:
- The study will be registered on ClinicalTrials.gov (or equivalent registry)
"""


def get_synopsis_templates() -> SynopsisTemplates:
    """
    Factory function to create a SynopsisTemplates instance.
    
    Returns:
        SynopsisTemplates instance
    """
    return SynopsisTemplates()
