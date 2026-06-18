from uuid import UUID, uuid4
from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base


class UserModel(Base):
    """Maps the application users table for authentication and ownership"""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)

    regions = relationship(
        "SpatialRegionModel", back_populates="owner", cascade="all, delete-orphan"
    )
