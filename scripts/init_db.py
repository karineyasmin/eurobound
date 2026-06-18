from app.core.database import engine, Base
from app.models import UserModel, SpatialRegionModel, PointOfInterestModel


def create_spatial_tables():
    print("=> Connecting to PostGIS and creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("🚀 Success! All spatial and core tables have been created.")


if __name__ == "__main__":
    create_spatial_tables()
