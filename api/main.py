"""
API endpoints using FastAPI for the oncology study management system.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging

from models.domain import Drug, ClinicalStudy, StudyDesign, Endpoint, PKProfile
from pk_data.source_pubmed import get_pk_data_source
from design.logic import get_design_selector
from stats.sample_size import get_sample_size_calculator
from reg.checks import get_regulatory_checker
from synopsis.generator import get_synopsis_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Oncology Clinical Trial Management API",
    description="API for managing oncology clinical trial protocols",
    version="1.0.0"
)


# Pydantic models for API requests/responses
class DrugRequest(BaseModel):
    name: str
    active_ingredient: str
    indication: str
    dosage_form: str
    route_of_administration: str
    manufacturer: Optional[str] = None


class StudyDesignRequest(BaseModel):
    number_of_treatments: int = 2
    study_duration_constraint: Optional[int] = None


class SampleSizeRequest(BaseModel):
    design_type: str
    effect_size: float
    std_dev: float
    number_of_arms: int = 2
    cv: Optional[float] = None


class StudyRequest(BaseModel):
    study_id: str
    title: str
    drug: DrugRequest
    design_type: Optional[str] = None
    endpoints: Optional[List[Dict]] = None


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Oncology Clinical Trial Management API",
        "version": "1.0.0",
        "endpoints": [
            "/pk-data",
            "/design/recommend",
            "/sample-size/calculate",
            "/regulatory/check",
            "/synopsis/generate"
        ]
    }


@app.post("/pk-data")
async def get_pk_data(drug: DrugRequest):
    """
    Retrieve PK data for a drug.
    
    Args:
        drug: Drug information
    
    Returns:
        PK profile data
    """
    try:
        logger.info(f"API: Getting PK data for {drug.name}")
        
        drug_obj = Drug(
            name=drug.name,
            active_ingredient=drug.active_ingredient,
            indication=drug.indication,
            dosage_form=drug.dosage_form,
            route_of_administration=drug.route_of_administration,
            manufacturer=drug.manufacturer
        )
        
        pk_source = get_pk_data_source()
        pk_profile = pk_source.search_pk_data(drug_obj)
        
        return {
            "drug": drug.name,
            "parameters": [
                {
                    "name": p.parameter_name,
                    "value": p.value,
                    "unit": p.unit,
                    "cv": p.coefficient_of_variation
                }
                for p in pk_profile.parameters
            ],
            "reference": pk_profile.study_reference
        }
    
    except Exception as e:
        logger.error(f"Error getting PK data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/design/recommend")
async def recommend_design(drug: DrugRequest, design_params: StudyDesignRequest):
    """
    Recommend a study design for a drug.
    
    Args:
        drug: Drug information
        design_params: Design parameters
    
    Returns:
        Recommended study design
    """
    try:
        logger.info(f"API: Recommending design for {drug.name}")
        
        drug_obj = Drug(
            name=drug.name,
            active_ingredient=drug.active_ingredient,
            indication=drug.indication,
            dosage_form=drug.dosage_form,
            route_of_administration=drug.route_of_administration
        )
        
        # Get PK data for better recommendations
        pk_source = get_pk_data_source()
        pk_profile = pk_source.search_pk_data(drug_obj)
        
        # Get design recommendation
        design_selector = get_design_selector()
        recommended_design = design_selector.recommend_design(
            drug=drug_obj,
            pk_profile=pk_profile,
            number_of_treatments=design_params.number_of_treatments,
            study_duration_constraint=design_params.study_duration_constraint
        )
        
        return {
            "design_type": recommended_design.design_type,
            "number_of_arms": recommended_design.number_of_arms,
            "treatment_duration": recommended_design.treatment_duration,
            "washout_period": recommended_design.washout_period,
            "blinding": recommended_design.blinding,
            "randomization": recommended_design.randomization
        }
    
    except Exception as e:
        logger.error(f"Error recommending design: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sample-size/calculate")
async def calculate_sample_size(params: SampleSizeRequest):
    """
    Calculate sample size for a study.
    
    Args:
        params: Sample size calculation parameters
    
    Returns:
        Sample size results
    """
    try:
        logger.info(f"API: Calculating sample size for {params.design_type} design")
        
        calculator = get_sample_size_calculator()
        
        if params.design_type == "parallel":
            result = calculator.calculate_parallel_design(
                effect_size=params.effect_size,
                std_dev=params.std_dev,
                number_of_arms=params.number_of_arms
            )
        elif params.design_type == "crossover":
            result = calculator.calculate_crossover_design(
                effect_size=params.effect_size,
                std_dev=params.std_dev
            )
        elif params.design_type == "bioequivalence" and params.cv:
            result = calculator.calculate_bioequivalence(
                cv=params.cv,
                design="crossover"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported design type: {params.design_type}"
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating sample size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regulatory/check")
async def check_regulatory_compliance(study_request: StudyRequest):
    """
    Check regulatory compliance for a study.
    
    Args:
        study_request: Study information
    
    Returns:
        Regulatory compliance check results
    """
    try:
        logger.info(f"API: Checking regulatory compliance for study {study_request.study_id}")
        
        # Create study object
        drug_obj = Drug(
            name=study_request.drug.name,
            active_ingredient=study_request.drug.active_ingredient,
            indication=study_request.drug.indication,
            dosage_form=study_request.drug.dosage_form,
            route_of_administration=study_request.drug.route_of_administration
        )
        
        study = ClinicalStudy(
            study_id=study_request.study_id,
            title=study_request.title,
            drug=drug_obj
        )
        
        # Add design if specified
        if study_request.design_type:
            study.design = StudyDesign(
                design_type=study_request.design_type,
                number_of_arms=2,
                treatment_duration=28
            )
        
        # Check compliance
        checker = get_regulatory_checker()
        violations = checker.check_study_compliance(study)
        
        return {
            "study_id": study.study_id,
            "compliant": len(violations) == 0,
            "violations": [
                {
                    "severity": v.severity,
                    "category": v.category,
                    "description": v.description,
                    "recommendation": v.recommendation
                }
                for v in violations
            ]
        }
    
    except Exception as e:
        logger.error(f"Error checking regulatory compliance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/synopsis/generate")
async def generate_synopsis(study_request: StudyRequest):
    """
    Generate a study synopsis.
    
    Args:
        study_request: Study information
    
    Returns:
        Generated synopsis text
    """
    try:
        logger.info(f"API: Generating synopsis for study {study_request.study_id}")
        
        # Create drug object
        drug_obj = Drug(
            name=study_request.drug.name,
            active_ingredient=study_request.drug.active_ingredient,
            indication=study_request.drug.indication,
            dosage_form=study_request.drug.dosage_form,
            route_of_administration=study_request.drug.route_of_administration
        )
        
        # Create study object
        study = ClinicalStudy(
            study_id=study_request.study_id,
            title=study_request.title,
            drug=drug_obj
        )
        
        # Add design if specified
        if study_request.design_type:
            study.design = StudyDesign(
                design_type=study_request.design_type,
                number_of_arms=2,
                treatment_duration=28
            )
        
        # Add endpoints if specified
        if study_request.endpoints:
            for ep_data in study_request.endpoints:
                endpoint = Endpoint(
                    name=ep_data.get("name", ""),
                    endpoint_type=ep_data.get("type", "primary"),
                    description=ep_data.get("description", "")
                )
                study.endpoints.append(endpoint)
        
        # Generate synopsis
        generator = get_synopsis_generator()
        synopsis = generator.generate_full_synopsis(study)
        
        return {
            "study_id": study.study_id,
            "synopsis": synopsis
        }
    
    except Exception as e:
        logger.error(f"Error generating synopsis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "oncology-trial-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
