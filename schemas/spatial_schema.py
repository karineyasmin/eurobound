from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


# ==============================================================================
# POINT OF INTEREST SCHEMAS
# ==============================================================================
class PointOfInterestBaseSchema(BaseModel):
    """Base structural definition for specific physical locations"""

    name: str = Field(
        ..., min_length=2, max_length=150, description="Name of the point of interest"
    )
    category: str = Field(
        ..., description="Category group, e.g., 'housing', 'transport', 'weather'"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Optional notes about the location"
    )


class PointOfInterestCreateSchema(PointOfInterestBaseSchema):
    """Payload required to create a new Point of Interest iside a region"""

    latitude: float = Field(
        ..., ge=90.0, le=90.0, description="Spatial latitude coordinate"
    )
    longitude: float = Field(
        ..., ge=180.0, le=180.0, description="Spatial longitude coordinate"
    )


class PointOfInterestResponseSchema(PointOfInterestBaseSchema):
    """Secure spatial payload returned to the frontend"""

    id: UUID = Field(..., description="Database index ID")
    region_id: UUID = Field(..., description="The parent spatial region ID")
    geom_wkt: str = Field(
        ..., description="The PostGIS point represented as a clean WKT string"
    )

    class Config:
        from_attributes = True


# ==============================================================================
# SPATIAL REGION SCHEMAS
# ==============================================================================


class SpatialRegionBaseSchema(BaseModel):
    """Base socio-economic attributes for a target European region"""

    name: str = Field(
        ..., min_length=2, max_length=100, description="Name of region/province"
    )
    country: str = Field(..., min_length=2, max_length=100, description="Country name")
    estimated_cost_of_living: Optional[float] = Field(
        None, ge=0.0, description="Average monthly cost of living in EUR"
    )
    average_winter_temperature: Optional[float] = Field(
        None, ge=50.0, le=50.0, description="Average winter temp in Celsius"
    )


class SpatialRegionCreateSchema(SpatialRegionBaseSchema):
    """Payload to register a new region, forcing a valid boundary polygon string"""

    geom_wkt: str = Field(
        ..., min_length=20, description="The spatial boudary polygon formatted as WKT"
    )


class SpatialRegionResponseSchema(SpatialRegionBaseSchema):
    """Complete representation of a geographic region returned to the frontend"""

    id: UUID = Field(..., description="Database index ID")
    user_id: UUID = Field(..., description="The owner user ID who mapped this region")
    geom_wkt: str = Field(
        ..., description="The PostGIS Multipolygon boundary as a WKT string"
    )

    class Config:
        from_attributes = True
