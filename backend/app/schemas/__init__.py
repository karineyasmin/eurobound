"""
Eurobound Data validation and Serealization Schemas Package.

This package centralizes all Pydantic V2 models used across the application.
These schemas act as strict contract gatekeepers, validating icoming JSON payloads
from the frontend and shaping secure outgoing HTTP responses
"""

from app.schemas.user_schema import (
    UserBaseSchema,
    UserCreateSchema,
    UserResponseSchema,
)
from app.schemas.spatial_schema import (
    PointOfInterestBaseSchema,
    PointOfInterestCreateSchema,
    PointOfInterestResponseSchema,
    SpatialRegionBaseSchema,
    SpatialRegionCreateSchema,
    SpatialRegionResponseSchema,
)

__all__ = [
    "UserBaseSchema",
    "UserCreateSchema",
    "UserResponseSchema",
    "PointOfInterestBaseSchema",
    "PointOfInterestCreateSchema",
    "PointOfInterestResponseSchema",
    "SpatialRegionBaseSchema",
    "SpatialRegionCreateSchema",
    "SpatialRegionResponseSchema",
]
