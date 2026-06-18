"""
EuroBound Database Models Package.

This package centralizes all SQLAlchemy and GeoAlchemy2 ORM models representing
the database architecture for users, spatial regions, and points of interest.
"""

from app.models.user_model import UserModel
from app.models.spatial_model import SpatialRegionModel, PointOfInterestModel

__all__ = [
    "UserModel",
    "SpatialRegionModel",
    "PointOfInterestModel",
]
