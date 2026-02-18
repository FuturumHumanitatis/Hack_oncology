"""
Demo workflow: omeprazole bioequivalence study (fasted, low CV).

The script performs the full pipeline:
1. Create StudyInput for omeprazole (fasted, cv_category="low")
2. Retrieve PK parameters via get_pk_parameters
3. Select a study design
4. Calculate sample size (N)
5. Run regulatory compliance checks
6. Generate a Markdown synopsis and save it to example_synopsis_omeprazole.md
"""
import logging
import os
from datetime import datetime

from models.domain import (
    StudyInput, ClinicalStudy, StudyPopulation, Endpoint,
)
from pk_data.source_pubmed import get_pk_parameters
from design.logic import get_design_selector
from stats.sample_size import get_sample_size_calculator
from reg.checks import get_regulatory_checker
from synopsis.generator import get_synopsis_generator

# Suppress verbose logs – only warnings and errors reach the console
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logging.getLogger().setLevel(logging.WARNING)


def _build_markdown(study, sample_size_result, violations, regulatory_body="FDA"):
    """Return a Markdown-formatted synopsis string."""
    lines = [
        f"# {study.title}",
        "",
        f"**Protocol:** {study.study_id}  ",
        f"**Drug:** {study.drug.name} ({study.drug.active_ingredient})  ",
        f"**Indication:** {study.drug.indication}  ",
        f"**Date:** {study.created_at.strftime('%Y-%m-%d')}",
        "",
        "## Background",
        "",
        (
            f"{study.drug.name} is a {study.drug.dosage_form} formulation "
            f"containing {study.drug.active_ingredient}, administered "
            f"via {study.drug.route_of_administration}."
        ),
        "",
    ]

    # PK parameters
    if study.pk_profile and study.pk_profile.parameters:
        lines.append("## PK Parameters")
        lines.append("")
        lines.append("| Parameter | Value | Unit | CV |")
        lines.append("|-----------|------:|------|---:|")
        for p in study.pk_profile.parameters:
            cv_pct = f"{p.coefficient_of_variation * 100:.0f}%" if p.coefficient_of_variation else "—"
            lines.append(f"| {p.parameter_name} | {p.value} | {p.unit} | {cv_pct} |")
        lines.append("")

    # Design
    if study.design:
        d = study.design
        lines.append("## Study Design")
        lines.append("")
        lines.append(f"- **Type:** {d.design_type}")
        lines.append(f"- **Arms:** {d.number_of_arms}")
        lines.append(f"- **Treatment duration:** {d.treatment_duration} days")
        lines.append(f"- **Blinding:** {d.blinding}")
        if d.washout_period:
            lines.append(f"- **Washout:** {d.washout_period} days")
        lines.append("")

    # Population
    if study.population:
        pop = study.population
        lines.append("## Study Population")
        lines.append("")
        lines.append(f"- Age: {pop.age_range[0]}–{pop.age_range[1]} years")
        lines.append(f"- Gender: {pop.gender}")
        if pop.inclusion_criteria:
            lines.append("")
            lines.append("**Inclusion criteria:**")
            for c in pop.inclusion_criteria:
                lines.append(f"- {c}")
        if pop.exclusion_criteria:
            lines.append("")
            lines.append("**Exclusion criteria:**")
            for c in pop.exclusion_criteria:
                lines.append(f"- {c}")
        lines.append("")

    # Sample size
    lines.append("## Sample Size")
    lines.append("")
    design_key = sample_size_result.get("design", "")
    if design_key == "crossover":
        lines.append(f"- **N (adjusted):** {sample_size_result['adjusted_n_subjects']}")
    else:
        lines.append(f"- **N per group (adjusted):** {sample_size_result['adjusted_n_per_group']}")
        lines.append(f"- **Total N (adjusted):** {sample_size_result['adjusted_total_n']}")
    lines.append(f"- α = {sample_size_result.get('alpha', 0.05)}")
    lines.append(f"- Power = {sample_size_result.get('power', 0.80)}")
    lines.append(f"- Dropout rate = {sample_size_result.get('dropout_rate', 0.15) * 100:.0f}%")
    lines.append("")

    # Regulatory
    lines.append("## Regulatory Compliance")
    lines.append("")
    if violations:
        for v in violations:
            lines.append(f"- **[{v.severity.upper()}]** {v.category}: {v.description}")
    else:
        lines.append("No issues found — study is compliant.")
    lines.append("")

    lines.append("---")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} "
                 f"for {regulatory_body} submission.*")
    lines.append("")

    return "\n".join(lines)


def main():
    """Run the omeprazole demo workflow."""

    # 1. Study input
    study_input = StudyInput(
        drug_name="Omeprazole",
        fasting=True,
        cv_category="low",
    )

    # 2. PK parameters
    pk_profile = get_pk_parameters(study_input)

    # 3. Select design
    design_selector = get_design_selector()
    design = design_selector.recommend_design(
        drug=pk_profile.drug,
        pk_profile=pk_profile,
        number_of_treatments=2,
    )

    # 4. Calculate sample size
    calculator = get_sample_size_calculator(alpha=0.05, power=0.80, dropout_rate=0.15)

    if design.design_type == "crossover":
        sample_size_result = calculator.calculate_crossover_design(
            effect_size=300.0,
            std_dev=500.0,
            correlation=0.6,
        )
        n_display = sample_size_result["adjusted_n_subjects"]
    else:
        sample_size_result = calculator.calculate_parallel_design(
            effect_size=300.0,
            std_dev=500.0,
            number_of_arms=design.number_of_arms,
        )
        n_display = sample_size_result["adjusted_total_n"]

    # 5. Regulatory checks
    population = StudyPopulation(
        age_range=(18, 55),
        gender="all",
        inclusion_criteria=[
            "Healthy volunteers",
            "BMI 18.5–30 kg/m²",
            "Non-smoker",
        ],
        exclusion_criteria=[
            "Known hypersensitivity to omeprazole",
            "Clinically significant illness within 4 weeks",
        ],
    )

    endpoints = [
        Endpoint(
            name="AUC₀₋t",
            endpoint_type="primary",
            description="Area under the plasma concentration–time curve",
            measurement_timepoints=[1, 2, 4, 8, 12, 24],
        ),
        Endpoint(
            name="Cmax",
            endpoint_type="primary",
            description="Peak plasma concentration",
            measurement_timepoints=[1, 2, 4, 8, 12, 24],
        ),
    ]

    study = ClinicalStudy(
        study_id="BE-OME-2024-001",
        title="Bioequivalence Study of Omeprazole 20 mg Capsules (Fasted)",
        drug=pk_profile.drug,
        pk_profile=pk_profile,
        design=design,
        population=population,
        endpoints=endpoints,
        sample_size=n_display,
        created_at=datetime.now(),
    )

    checker = get_regulatory_checker(regulatory_body="FDA")
    violations = checker.check_study_compliance(study)

    # 6. Generate Markdown synopsis
    synopsis_md = _build_markdown(study, sample_size_result, violations)

    # 7. Save to file
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "example_synopsis_omeprazole.md",
    )
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(synopsis_md)

    # Console summary (brief)
    print(f"Design : {design.design_type}")
    print(f"N      : {n_display}")
    print(f"Issues : {len(violations)}")
    print(f"Synopsis saved to {output_path}")


if __name__ == "__main__":
    main()
