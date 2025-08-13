from fastapi import APIRouter

from app.api_mongo.v1.endpoints import (
    areas,
    search,
    wellbeing,
    simulation,
    admin,
    waste_separation,
    congestion
)

api_router = APIRouter()

api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(wellbeing.router, prefix="/wellbeing", tags=["wellbeing"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(waste_separation.router, prefix="/waste-separation", tags=["waste"])
api_router.include_router(congestion.router, prefix="/congestion", tags=["congestion"])