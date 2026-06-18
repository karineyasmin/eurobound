from uuid import UUID, uuid4
from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from geoalchemy2 import Geometry, WKTElement
from app.core.database import Base
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_model import UserModel


class SpatialRegionModel(Base):
    """Maps European target regions with spatial boundary polygons"""

    __tablename__ = "spatial_regions"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    estimated_cost_of_living: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    average_winter_temperature: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, default=uuid4
    )

    geom: Mapped[WKTElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False
    )
    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="regions")
    points_of_interest: Mapped[list["PointOfInterestModel"]] = relationship(
        "PointsOfInterestModel", back_populates="region"
    )


class PointOfInterestModel(Base):
    """Maps specific points (houses, stations) inside a spatial region"""

    __tablename__ = "points_of_interest"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    region_id: Mapped[UUID] = mapped_column(
        Integer, ForeignKey("spatial_regions.id"), nullable=False
    )

    geom: Mapped[WKTElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )
    region: Mapped["SpatialRegionModel"] = relationship(
        "SpatialRegionModel", back_populates="points_of_interest"
    )
