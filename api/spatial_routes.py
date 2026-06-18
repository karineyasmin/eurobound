from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement
from app.core import get_db_session
from app.core import logger
from app.models import SpatialRegionModel, PointOfInterestModel
from app.schemas import (
    SpatialRegionCreateSchema,
    SpatialRegionResponseSchema,
    PointOfInterestCreateSchema,
    PointOfInterestResponseSchema,
)

spatial_router: APIRouter = APIRouter(tags=["Spatial Operations"])


@spatial_router.post(
    "regions",
    response_model=SpatialRegionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_spatial_region(
    region_data: SpatialRegionCreateSchema,
    user_id: int,
    db_session: Session = Depends(get_db_session),
) -> SpatialRegionModel:
    """
    Registers a new European target region with a spatial MultiPolygon boundary.
    Converts incoming WKT string into a PostGIS geometry element.
    """
    logger.info(
        f"Registering spatial region '{region_data.name}' for user ID {user_id}"
    )
    try:
        spatial_geom: WKTElement = WKTElement(region_data.geom_wkt, srid=4326)

        new_region: SpatialRegionModel = SpatialRegionModel(
            name=region_data.name,
            country=region_data.country,
            estimated_cost_of_living=region_data.estimated_cost_of_living,
            average_winter_temperature=region_data.average_winter_temperature,
            user_id=user_id,
            geom=spatial_geom,
        )

        db_session.add(new_region)
        db_session.commit()
        db_session.refresh(new_region)

        new_region.geom_wkt = region_data.geom_wkt
        logger.info(f"Spatial region successfully saved with ID: {new_region.id}")
        return new_region

    except IntegrityError as error:
        db_session.rollback()
        logger.warning(
            f"Database Integrity Error: User ID {user_id} probably does not exist. Details: {str(error)}"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid spatial geometry format. Check your WKT string.",
        )


@spatial_router.post(
    "/pois/",
    response_model=PointOfInterestResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_point_of_interest(
    poi_data: PointOfInterestCreateSchema,
    region_id: int,
    db_session: Session = Depends(get_db_session),
) -> PointOfInterestModel:
    """
    Creates a specific point of interest (e.g., housing, school) inside a region.
    Constructs a WKT POINT string dynamically from latitude and longitude inputs.
    """
    logger.info(f"Adding POI '{poi_data.name}' under category '{poi_data.category}'")
    try:
        wkt_point: str = f"POINT({poi_data.longitude} {poi_data.latitude})"
        spatial_geom: WKTElement = WKTElement(wkt_point, srid=4326)

        new_poi: PointOfInterestModel = PointOfInterestModel(
            name=poi_data.name,
            category=poi_data.category,
            description=poi_data.description,
            region_id=region_id,
            geom=spatial_geom,
        )

        db_session.add(new_poi)
        db_session.commit()
        db_session.refresh(new_poi)

        new_poi.geom_wkt = wkt_point
        return new_poi
    except IntegrityError as error:
        db_session.rollback()
        logger.warning(
            f"Database Integrity Error: Region ID {region_id} does not exist. Details: {str(error)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create POI. Ensure the provided region_id exists.",
        )
    except SQLAlchemyError as error:
        db_session.rollback()
        logger.error(
            f"Database transaction failed while saving POI. Details: {str(error)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database transaction failure.",
        )
