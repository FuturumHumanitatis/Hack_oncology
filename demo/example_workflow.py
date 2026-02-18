"""
End-to-end demonstration workflow for the oncology clinical trial management system.
This script demonstrates the complete workflow from drug definition to synopsis generation.
"""
import logging
from datetime import datetime

from models.domain import (
    Drug, ClinicalStudy, StudyDesign, StudyPopulation, Endpoint
)
from pk_data.source_pubmed import get_pk_data_source
from design.logic import get_design_selector
from stats.sample_size import get_sample_size_calculator
from reg.checks import get_regulatory_checker
from synopsis.generator import get_synopsis_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main demonstration workflow.
    """
    logger.info("=" * 80)
    logger.info("ONCOLOGY CLINICAL TRIAL MANAGEMENT SYSTEM - DEMO WORKFLOW")
    logger.info("=" * 80)
    
    # Step 1: Define the drug
    logger.info("\nSTEP 1: Define the investigational drug")
    logger.info("-" * 80)
    
    drug = Drug(
        name="Onco-Therapy X",
        active_ingredient="Compound-123",
        indication="Advanced Non-Small Cell Lung Cancer (NSCLC)",
        dosage_form="Oral tablet",
        route_of_administration="Oral",
        manufacturer="Pharma Corp Ltd.",
        approval_status="Investigational"
    )
    
    logger.info(f"Drug defined: {drug}")
    logger.info(f"  - Active ingredient: {drug.active_ingredient}")
    logger.info(f"  - Indication: {drug.indication}")
    logger.info(f"  - Dosage form: {drug.dosage_form}")
    
    # Step 2: Retrieve PK data
    logger.info("\nSTEP 2: Retrieve pharmacokinetic (PK) data")
    logger.info("-" * 80)
    
    pk_source = get_pk_data_source()
    pk_profile = pk_source.search_pk_data(drug)
    
    logger.info(f"PK profile retrieved for {drug.name}")
    logger.info(f"  - Number of parameters: {len(pk_profile.parameters)}")
    for param in pk_profile.parameters:
        logger.info(f"  - {param}")
    
    # Step 3: Select study design
    logger.info("\nSTEP 3: Select appropriate study design")
    logger.info("-" * 80)
    
    design_selector = get_design_selector()
    recommended_design = design_selector.recommend_design(
        drug=drug,
        pk_profile=pk_profile,
        number_of_treatments=2,
        study_duration_constraint=60
    )
    
    logger.info(f"Recommended design: {recommended_design}")
    logger.info(f"  - Design type: {recommended_design.design_type}")
    logger.info(f"  - Number of arms: {recommended_design.number_of_arms}")
    logger.info(f"  - Treatment duration: {recommended_design.treatment_duration} days")
    logger.info(f"  - Blinding: {recommended_design.blinding}")
    
    # Validate the design
    is_valid, warnings = design_selector.validate_design(recommended_design)
    logger.info(f"  - Design validation: {'Valid' if is_valid else 'Invalid'}")
    if warnings:
        for warning in warnings:
            logger.warning(f"    ! {warning}")
    
    # Step 4: Calculate sample size
    logger.info("\nSTEP 4: Calculate required sample size")
    logger.info("-" * 80)
    
    calculator = get_sample_size_calculator(alpha=0.05, power=0.80, dropout_rate=0.15)
    
    # Get CV from PK data for calculation
    auc_param = pk_profile.get_parameter("AUC")
    cv = auc_param.coefficient_of_variation if auc_param else 0.25
    
    if recommended_design.design_type == "crossover":
        sample_size_result = calculator.calculate_crossover_design(
            effect_size=300.0,  # Expected difference in AUC
            std_dev=500.0,
            correlation=0.6
        )
    else:  # parallel
        sample_size_result = calculator.calculate_parallel_design(
            effect_size=300.0,
            std_dev=500.0,
            number_of_arms=recommended_design.number_of_arms
        )
    
    logger.info("Sample size calculated:")
    if recommended_design.design_type == "crossover":
        logger.info(f"  - Subjects needed: {sample_size_result['adjusted_n_subjects']}")
    else:
        logger.info(f"  - Per group: {sample_size_result['adjusted_n_per_group']}")
        logger.info(f"  - Total: {sample_size_result['adjusted_total_n']}")
    logger.info(f"  - Power: {sample_size_result['power']}")
    logger.info(f"  - Alpha: {sample_size_result['alpha']}")
    
    # Step 5: Define study population
    logger.info("\nSTEP 5: Define study population")
    logger.info("-" * 80)
    
    population = StudyPopulation(
        age_range=(18, 75),
        gender="all",
        disease_stage="Stage IIIB or IV NSCLC",
        prior_treatment="At least one prior platinum-based chemotherapy",
        inclusion_criteria=[
            "Histologically confirmed NSCLC",
            "ECOG performance status 0-1",
            "Adequate organ function",
            "Life expectancy ≥ 3 months"
        ],
        exclusion_criteria=[
            "Brain metastases (unless treated and stable)",
            "Uncontrolled concurrent illness",
            "Prior treatment with Compound-123",
            "Pregnancy or lactation"
        ]
    )
    
    logger.info(f"Population defined:")
    logger.info(f"  - Age range: {population.age_range[0]}-{population.age_range[1]} years")
    logger.info(f"  - Gender: {population.gender}")
    logger.info(f"  - Disease stage: {population.disease_stage}")
    logger.info(f"  - Inclusion criteria: {len(population.inclusion_criteria)} items")
    logger.info(f"  - Exclusion criteria: {len(population.exclusion_criteria)} items")
    
    # Step 6: Define study endpoints
    logger.info("\nSTEP 6: Define study endpoints")
    logger.info("-" * 80)
    
    endpoints = [
        Endpoint(
            name="Overall Response Rate (ORR)",
            endpoint_type="primary",
            description="Proportion of patients with complete or partial response",
            measurement_timepoints=[28, 56, 84]
        ),
        Endpoint(
            name="Progression-Free Survival (PFS)",
            endpoint_type="secondary",
            description="Time from randomization to disease progression or death",
            measurement_timepoints=[28, 56, 84, 112, 140, 168]
        ),
        Endpoint(
            name="Safety and Tolerability",
            endpoint_type="secondary",
            description="Incidence and severity of adverse events",
            measurement_timepoints=[7, 14, 21, 28, 56, 84]
        )
    ]
    
    logger.info(f"Endpoints defined: {len(endpoints)}")
    for endpoint in endpoints:
        logger.info(f"  - {endpoint}")
    
    # Step 7: Create complete study
    logger.info("\nSTEP 7: Create complete clinical study")
    logger.info("-" * 80)
    
    study = ClinicalStudy(
        study_id="ONCO-X-2024-001",
        title="A Phase II Study of Onco-Therapy X in Patients with Advanced NSCLC",
        drug=drug,
        pk_profile=pk_profile,
        design=recommended_design,
        population=population,
        endpoints=endpoints,
        sample_size=sample_size_result.get('adjusted_total_n') or sample_size_result.get('adjusted_n_subjects'),
        created_at=datetime.now()
    )
    
    logger.info(f"Study created: {study}")
    logger.info(f"  - Study ID: {study.study_id}")
    logger.info(f"  - Sample size: {study.sample_size}")
    
    # Step 8: Regulatory compliance check
    logger.info("\nSTEP 8: Perform regulatory compliance check")
    logger.info("-" * 80)
    
    checker = get_regulatory_checker(regulatory_body="FDA")
    violations = checker.check_study_compliance(study)
    
    logger.info(f"Regulatory compliance check completed:")
    logger.info(f"  - Violations found: {len(violations)}")
    
    if violations:
        for violation in violations:
            logger.warning(
                f"  - [{violation.severity.upper()}] {violation.category}: "
                f"{violation.description}"
            )
    else:
        logger.info("  - No violations found - study is compliant!")
    
    # Get GCP compliance status
    gcp_compliance = checker.check_gcp_compliance(study)
    logger.info(f"\nGCP Compliance Requirements:")
    for requirement, status in gcp_compliance.items():
        status_str = "✓" if status else "✗"
        logger.info(f"  {status_str} {requirement.replace('_', ' ').title()}")
    
    # Step 9: Generate synopsis
    logger.info("\nSTEP 9: Generate study synopsis")
    logger.info("-" * 80)
    
    generator = get_synopsis_generator()
    synopsis = generator.generate_full_synopsis(
        study=study,
        sample_size_result=sample_size_result,
        regulatory_body="FDA"
    )
    
    logger.info("Synopsis generated successfully")
    logger.info(f"  - Synopsis length: {len(synopsis)} characters")
    
    # Save synopsis to file
    output_filename = f"/tmp/synopsis_{study.study_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    generator.export_to_file(
        study=study,
        filename=output_filename,
        sample_size_result=sample_size_result,
        regulatory_body="FDA"
    )
    
    logger.info(f"  - Synopsis saved to: {output_filename}")
    
    # Display synopsis preview
    logger.info("\nSYNOPSIS PREVIEW:")
    logger.info("=" * 80)
    print("\n" + synopsis[:1500] + "\n... [truncated for display] ...\n")
    
    # Step 10: Summary
    logger.info("\nSTEP 10: Generate study summary")
    logger.info("-" * 80)
    
    summary = generator.generate_summary(study)
    logger.info("Study Summary:")
    for key, value in summary.items():
        logger.info(f"  - {key}: {value}")
    
    # Final message
    logger.info("\n" + "=" * 80)
    logger.info("DEMO WORKFLOW COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)
    logger.info(f"\nFull synopsis available at: {output_filename}")
    logger.info("\nNext steps:")
    logger.info("  1. Review the generated synopsis")
    logger.info("  2. Address any regulatory violations")
    logger.info("  3. Submit for ethics committee review")
    logger.info("  4. Register the trial on ClinicalTrials.gov")
    logger.info("  5. Obtain regulatory approval before study initiation")
    logger.info("")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error in demo workflow: {str(e)}", exc_info=True)
        raise
