"""
EuroBound API Controllers and Routers Package.

This package contains all the HTTP endpoints (controllers) divided by domain.
It handles requests, triggers database transactions, and manages response serialization.
"""

from app.api.user_routes import user_router
from app.api.spatial_routes import spatial_router


__all__ = ["user_router", "spatial_router"]
