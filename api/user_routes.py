from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.core.database import get_db_session
from app.core.logger import logger
from app.models.user_model import UserModel
from app.schemas import UserCreateSchema, UserResponseSchema

user_router: APIRouter = APIRouter(prefix="/users", tags=["Users"])


@user_router.post(
    "/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreateSchema, db_session: AsyncSession = Depends(get_db_session)
) -> UserResponseSchema:
    """
    Registers a new user asynchronously.
    Uses managed transactions via db_session.begin() for automatic rollback safety.
    """
    logger.info(f"Initiating async user registration process for: {user_data.email}")

    try:
        statement: Select[tuple[UserModel]] = select(UserModel).where(
            UserModel.email == user_data.email
        )

        # 1. Read operations do not require a transaction block
        result = await db_session.execute(statement)
        existing_user: UserModel | None = result.scalar_one_or_none()

        if existing_user:
            logger.warning(
                f"Registration aborted: Email '{user_data.email}' already exists in database."
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

        # 2. Write operations inside a managed block (Automatic Commit/Rollback)
        async with db_session.begin():
            db_session.add(new_user)
            logger.debug(f"User database state staged for email: {user_data.email}")

        # 3. Refresh happens after the transaction block closes successfully
        await db_session.refresh(new_user)

        logger.info(
            f"User '{user_data.email}' successfully registered with internal ID: {new_user.id}"
        )

        return UserResponseSchema(
            id=new_user.id, email=new_user.email, full_name=new_user.full_name
        )

    except IntegrityError as error:
        # Managed block already handles rollback, we just log and translate the exception
        logger.error(
            f"Transaction collapsed due to database integrity violation: {str(error)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Check unique constraints.",
        )
    except SQLAlchemyError as error:
        logger.critical(
            f"Fatal database error during user creation transaction: {str(error)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal database operation failure.",
        )


@user_router.get("/", response_model=List[UserResponseSchema])
async def list_users(
    db_session: AsyncSession = Depends(get_db_session),
) -> List[UserResponseSchema]:
    """
    Retrieves all registered users asynchronously.
    """
    logger.debug("Executing async query to fetch all system users.")

    try:
        statement: Select[tuple[UserModel]] = select(UserModel)
        result = await db_session.execute(statement)
        users: List[UserModel] = list(result.scalars().all())

        logger.info(f"User list fetched successfully. Total records: {len(users)}")

        # Mapping model objects to schemas explicitly
        return [
            UserResponseSchema(id=u.id, email=u.email, full_name=u.full_name)
            for u in users
        ]

    except SQLAlchemyError as error:
        logger.error(f"Failed to compile or execute users query. Details: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user records from database.",
        )
