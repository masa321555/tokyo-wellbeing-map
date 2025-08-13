from fastapi import APIRouter

from app.api.v1.endpoints_mongo import (
    areas,
    search,
    wellbeing,
    simulation,
    recommendations,
    age_distribution,
    waste_separation,
    congestion
)

api_router = APIRouter()

api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(wellbeing.router, prefix="/wellbeing", tags=["wellbeing"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(age_distribution.router, prefix="/age-distribution", tags=["age-distribution"])
api_router.include_router(waste_separation.router, prefix="/waste-separation", tags=["waste-separation"])
api_router.include_router(congestion.router, prefix="/congestion", tags=["congestion"])