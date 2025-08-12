from fastapi import APIRouter

from app.api.v1.endpoints import areas, search, wellbeing, simulation, opendata, places, congestion, admin

api_router = APIRouter()

api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(wellbeing.router, prefix="/wellbeing", tags=["wellbeing"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
api_router.include_router(opendata.router, prefix="/opendata", tags=["opendata"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(congestion.router, prefix="/congestion", tags=["congestion"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])