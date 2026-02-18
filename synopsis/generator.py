"""
Synopsis generator for assembling complete clinical trial synopses.
"""
from typing import Optional, Dict
import logging

from models.domain import ClinicalStudy
from synopsis.templates import SynopsisTemplates, get_synopsis_templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SynopsisGenerator:
    """
    Generator for creating complete clinical trial synopses.
    """
    
    def __init__(self):
        self.templates = get_synopsis_templates()
        logger.info("SynopsisGenerator initialized")
    
    def generate_full_synopsis(
        self,
        study: ClinicalStudy,
        sample_size_result: Optional[Dict] = None,
        regulatory_body: str = "FDA"
    ) -> str:
        """
        Generate a complete study synopsis.
        
        Args:
            study: Clinical study object
            sample_size_result: Sample size calculation results (optional)
            regulatory_body: Regulatory body for compliance (default: FDA)
        
        Returns:
            Complete synopsis as formatted text
        """
        logger.info(f"Generating full synopsis for study {study.study_id}")
        
        synopsis_parts = []
        
        # Title section
        synopsis_parts.append(self.templates.title_section(study))
        synopsis_parts.append("\n" + "=" * 80 + "\n")
        
        # Background
        synopsis_parts.append(self.templates.background_section(study.drug))
        synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Objectives
        if study.endpoints:
            synopsis_parts.append(self.templates.objectives_section(study.endpoints))
            synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Study Design
        if study.design:
            synopsis_parts.append(self.templates.study_design_section(study.design))
            synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Study Population
        synopsis_parts.append(self.templates.study_population_section(study.population))
        synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Treatment
        if study.design:
            synopsis_parts.append(self.templates.treatment_section(study.drug, study.design))
            synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Endpoints
        if study.endpoints:
            synopsis_parts.append(self.templates.endpoints_section(study.endpoints))
            synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Statistical Analysis
        if study.design:
            synopsis_parts.append(
                self.templates.statistical_analysis_section(study.design, study.sample_size)
            )
            synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Sample Size
        if sample_size_result:
            synopsis_parts.append(self.templates.sample_size_section(sample_size_result))
            synopsis_parts.append("\n" + "-" * 80 + "\n")
        
        # Regulatory
        synopsis_parts.append(self.templates.regulatory_section(regulatory_body))
        synopsis_parts.append("\n" + "=" * 80 + "\n")
        
        # Combine all parts
        full_synopsis = "".join(synopsis_parts)
        
        logger.info("Synopsis generation completed")
        return full_synopsis
    
    def generate_section(
        self,
        section_name: str,
        study: ClinicalStudy,
        sample_size_result: Optional[Dict] = None,
        regulatory_body: str = "FDA"
    ) -> str:
        """
        Generate a specific section of the synopsis.
        
        Args:
            section_name: Name of the section to generate
            study: Clinical study object
            sample_size_result: Sample size calculation results (optional)
            regulatory_body: Regulatory body for compliance
        
        Returns:
            Section text
        """
        logger.info(f"Generating section: {section_name}")
        
        section_map = {
            "title": lambda: self.templates.title_section(study),
            "background": lambda: self.templates.background_section(study.drug),
            "objectives": lambda: self.templates.objectives_section(study.endpoints),
            "study_design": lambda: self.templates.study_design_section(study.design),
            "study_population": lambda: self.templates.study_population_section(study.population),
            "treatment": lambda: self.templates.treatment_section(study.drug, study.design),
            "endpoints": lambda: self.templates.endpoints_section(study.endpoints),
            "statistical_analysis": lambda: self.templates.statistical_analysis_section(
                study.design, study.sample_size
            ),
            "sample_size": lambda: self.templates.sample_size_section(sample_size_result),
            "regulatory": lambda: self.templates.regulatory_section(regulatory_body)
        }
        
        if section_name not in section_map:
            logger.error(f"Unknown section: {section_name}")
            raise ValueError(f"Unknown section: {section_name}")
        
        return section_map[section_name]()
    
    def export_to_file(
        self,
        study: ClinicalStudy,
        filename: str,
        sample_size_result: Optional[Dict] = None,
        regulatory_body: str = "FDA"
    ) -> None:
        """
        Export synopsis to a text file.
        
        Args:
            study: Clinical study object
            filename: Output filename
            sample_size_result: Sample size calculation results (optional)
            regulatory_body: Regulatory body for compliance
        """
        logger.info(f"Exporting synopsis to file: {filename}")
        
        synopsis = self.generate_full_synopsis(study, sample_size_result, regulatory_body)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(synopsis)
        
        logger.info(f"Synopsis exported successfully to {filename}")
    
    def generate_summary(self, study: ClinicalStudy) -> Dict[str, str]:
        """
        Generate a summary of key study information.
        
        Args:
            study: Clinical study object
        
        Returns:
            Dictionary with summary information
        """
        summary = {
            "study_id": study.study_id,
            "title": study.title,
            "drug": str(study.drug),
            "design": str(study.design) if study.design else "Not specified",
            "sample_size": str(study.sample_size) if study.sample_size else "Not calculated",
            "num_endpoints": str(len(study.endpoints)) if study.endpoints else "0"
        }
        
        return summary


def get_synopsis_generator() -> SynopsisGenerator:
    """
    Factory function to create a SynopsisGenerator instance.
    
    Returns:
        SynopsisGenerator instance
    """
    return SynopsisGenerator()
