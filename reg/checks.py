"""
Regulatory checks and compliance validation for clinical trials.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

from models.domain import ClinicalStudy, StudyDesign, Endpoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RegulatoryViolation:
    """Represents a regulatory compliance violation."""
    severity: str  # "critical", "major", "minor"
    category: str
    description: str
    recommendation: str


class RegulatoryChecker:
    """
    Service for checking regulatory compliance of clinical trial protocols.
    """
    
    def __init__(self, regulatory_body: str = "FDA"):
        """
        Initialize regulatory checker.
        
        Args:
            regulatory_body: Regulatory body to check against (FDA, EMA, NMPA, etc.)
        """
        self.regulatory_body = regulatory_body
        logger.info(f"RegulatoryChecker initialized for {regulatory_body}")
    
    def check_study_compliance(self, study: ClinicalStudy) -> List[RegulatoryViolation]:
        """
        Perform comprehensive regulatory compliance check.
        
        Args:
            study: Clinical study to check
        
        Returns:
            List of regulatory violations (empty if compliant)
        """
        logger.info(f"Checking regulatory compliance for study {study.study_id}")
        
        violations = []
        
        # Check study identification
        violations.extend(self._check_study_identification(study))
        
        # Check study design
        if study.design:
            violations.extend(self._check_study_design(study.design))
        
        # Check endpoints
        violations.extend(self._check_endpoints(study.endpoints))
        
        # Check sample size
        violations.extend(self._check_sample_size(study))
        
        # Check informed consent requirements
        violations.extend(self._check_informed_consent(study))
        
        logger.info(f"Found {len(violations)} compliance issues")
        return violations
    
    def _check_study_identification(self, study: ClinicalStudy) -> List[RegulatoryViolation]:
        """Check study identification requirements."""
        violations = []
        
        if not study.study_id or len(study.study_id) < 5:
            violations.append(RegulatoryViolation(
                severity="critical",
                category="identification",
                description="Study ID is missing or too short",
                recommendation="Provide a valid study identifier (e.g., protocol number)"
            ))
        
        if not study.title or len(study.title) < 10:
            violations.append(RegulatoryViolation(
                severity="major",
                category="identification",
                description="Study title is missing or insufficient",
                recommendation="Provide a descriptive study title"
            ))
        
        return violations
    
    def _check_study_design(self, design: StudyDesign) -> List[RegulatoryViolation]:
        """Check study design requirements."""
        violations = []
        
        # Check blinding
        if design.blinding not in ["single-blind", "double-blind"]:
            violations.append(RegulatoryViolation(
                severity="minor",
                category="design",
                description=f"Open-label design may require additional justification",
                recommendation="Consider blinding or provide rationale for open-label"
            ))
        
        # Check randomization
        if not design.randomization:
            violations.append(RegulatoryViolation(
                severity="major",
                category="design",
                description="Non-randomized design",
                recommendation="Randomization is strongly recommended for regulatory approval"
            ))
        
        # Check crossover washout
        if design.design_type == "crossover" and not design.washout_period:
            violations.append(RegulatoryViolation(
                severity="major",
                category="design",
                description="Crossover design missing washout period",
                recommendation="Specify adequate washout period (typically 5 half-lives)"
            ))
        
        return violations
    
    def _check_endpoints(self, endpoints: List[Endpoint]) -> List[RegulatoryViolation]:
        """Check endpoint requirements."""
        violations = []
        
        if not endpoints:
            violations.append(RegulatoryViolation(
                severity="critical",
                category="endpoints",
                description="No endpoints defined",
                recommendation="Define at least one primary endpoint"
            ))
            return violations
        
        # Check for primary endpoint
        primary_endpoints = [e for e in endpoints if e.endpoint_type == "primary"]
        if not primary_endpoints:
            violations.append(RegulatoryViolation(
                severity="critical",
                category="endpoints",
                description="No primary endpoint defined",
                recommendation="Define at least one primary endpoint"
            ))
        
        # Check for too many primary endpoints
        if len(primary_endpoints) > 2:
            violations.append(RegulatoryViolation(
                severity="minor",
                category="endpoints",
                description="Multiple primary endpoints may complicate analysis",
                recommendation="Consider limiting to 1-2 primary endpoints"
            ))
        
        return violations
    
    def _check_sample_size(self, study: ClinicalStudy) -> List[RegulatoryViolation]:
        """Check sample size requirements."""
        violations = []
        
        if not study.sample_size or study.sample_size < 10:
            violations.append(RegulatoryViolation(
                severity="major",
                category="sample_size",
                description="Sample size is missing or too small",
                recommendation="Provide justified sample size calculation"
            ))
        
        return violations
    
    def _check_informed_consent(self, study: ClinicalStudy) -> List[RegulatoryViolation]:
        """Check informed consent requirements."""
        violations = []
        
        # This is a placeholder - in real implementation would check actual consent forms
        logger.info("Informed consent check: placeholder implementation")
        
        return violations
    
    def check_gcp_compliance(self, study: ClinicalStudy) -> Dict[str, bool]:
        """
        Check Good Clinical Practice (GCP) compliance.
        
        Args:
            study: Clinical study to check
        
        Returns:
            Dictionary with GCP compliance status for different categories
        """
        logger.info("Checking GCP compliance")
        
        compliance = {
            "protocol_available": bool(study.title and study.study_id),
            "ethics_approval_required": True,
            "informed_consent_required": True,
            "data_management_plan_required": True,
            "monitoring_plan_required": True,
            "investigator_qualification_required": True,
            "adverse_event_reporting_required": True
        }
        
        return compliance
    
    def generate_regulatory_checklist(self, study: ClinicalStudy) -> Dict[str, List[str]]:
        """
        Generate a regulatory checklist for the study.
        
        Args:
            study: Clinical study
        
        Returns:
            Dictionary with checklist items by category
        """
        checklist = {
            "protocol": [
                "Protocol title and version",
                "Study objectives",
                "Study design description",
                "Patient population definition",
                "Inclusion/exclusion criteria",
                "Treatment plan",
                "Endpoints definition",
                "Sample size justification",
                "Statistical analysis plan"
            ],
            "ethics": [
                "IRB/IEC approval",
                "Informed consent form",
                "Patient information sheet"
            ],
            "regulatory": [
                f"{self.regulatory_body} IND/CTA submission",
                "Clinical trial registration (e.g., ClinicalTrials.gov)",
                "Insurance/indemnity",
                "Investigator's Brochure"
            ],
            "quality": [
                "Standard Operating Procedures (SOPs)",
                "Case Report Forms (CRFs)",
                "Data management plan",
                "Monitoring plan",
                "Quality control procedures"
            ],
            "safety": [
                "Adverse event definitions",
                "Safety monitoring plan",
                "DSMB charter (if applicable)",
                "Stopping rules"
            ]
        }
        
        return checklist


def get_regulatory_checker(regulatory_body: str = "FDA") -> RegulatoryChecker:
    """
    Factory function to create a RegulatoryChecker instance.
    
    Args:
        regulatory_body: Regulatory body (FDA, EMA, NMPA, etc.)
    
    Returns:
        RegulatoryChecker instance
    """
    return RegulatoryChecker(regulatory_body=regulatory_body)
