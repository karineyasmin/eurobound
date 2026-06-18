from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, Select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.core.database import get_db_session
from app.core.logger import logger
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreateSchema, UserResponseSchema

user_router: APIRouter = APIRouter(prefix="/users", tags=["Users"])


@user_router.post(
    "/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: UserCreateSchema, db_session: Session = Depends(get_db_session)
) -> UserModel:
    """Registers a new user in the system after validating uniqueness via stric schemas"""

    logger.info(f"Attemping to register user with email: {user_data.email}")

    try:
        statement: Select[tuple[UserModel]] = select(UserModel).where(
            UserModel.email == user_data.email
        )
        result = db_session.execute(statement)
        existing_user: UserModel | None = result.scalar_one_or_none()

        if existing_user:
            logger.warning(
                f"Registration failed: Email {user_data.email} is already taken."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )

        new_user: UserModel = UserModel(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=user_data.password,
        )

        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)

        return new_user

    except IntegrityError as error:
        db_session.rollback()
        logger.error(f"Database integrity violation while creating user: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Check input unique constraints.",
        )
    except SQLAlchemyError as error:
        db_session.rollback()
        logger.error(f"Database transaction failure on user creation: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database operation failure.",
        )


@user_router.get("/", response_model=list[UserResponseSchema])
def list_users(db_session: Session = Depends(get_db_session)) -> list[UserModel]:
    """
    Retrieves all users from the database, wrapped in a strict transaction guard.
    """

    logger.debug("Fetching all registered users from database.")

    try:
        statement: Select[tuple[UserModel]] = select(UserModel)
        result = db_session.execute(statement)
        users: list[UserModel] = list(result.scalars().all())

        logger.info(f"Successfully retrieved {len(users)} user records.")
        return users

    except SQLAlchemyError as error:
        logger.error(f"Failed to query users database table. Details: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user records from databas",
        )
