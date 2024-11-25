from sqlalchemy.orm import Session
from ..models.models import UserModel, UserDetailsModel, BodyMeasurementsModel, StylePreferencesModel, BudgetModel, ShoppingHabitsModel, UserPreferencesModel
from ..schemas.schemas import UserCreateSchema, UserUpdateSchema
from ..auth.jwt_handler import ALGORITHM, REFRESH_SECRET_KEY, get_password_hash
from jose import jwt
from datetime import datetime
from ..models.refresh_token import RefreshToken

def create_refresh_token(db: Session, user_id: int, token: str):
    # Decode token to get JTI and expiration
    payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    jti = payload["jti"]
    exp = datetime.fromtimestamp(payload["exp"])
    
    refresh_token = RefreshToken(
        user_id=user_id,
        token_id=jti,
        expires_at=exp
    )
    db.add(refresh_token)
    db.commit()
    return refresh_token

def get_refresh_token(db: Session, token_id: str):
    return db.query(RefreshToken).filter(
        RefreshToken.token_id == token_id,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

def invalidate_refresh_token(db: Session, user_id: int):
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    db.commit()
    
    
def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreateSchema):
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user_id: int, user_update: UserUpdateSchema):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    try:
        # Update UserDetailsModel
        if user_update.user_details:
            if not db_user.user_details:
                # Create new UserDetailsModel if it doesn't exist
                user_details = UserDetailsModel(
                    user_id=user_id,
                    **user_update.user_details.dict(exclude={'body_measurements', 'style_preferences'})
                )
                db.add(user_details)
                db.flush()  # Flush to get the user_details.id
            else:
                # Update existing UserDetailsModel
                for key, value in user_update.user_details.dict(exclude={'body_measurements', 'style_preferences'}).items():
                    setattr(db_user.user_details, key, value)

            # Ensure user_details is attached to db_user
            if not db_user.user_details:
                db.refresh(db_user)

            # Handle BodyMeasurementsModel
            if user_update.user_details.body_measurements:
                if not hasattr(db_user.user_details, 'body_measurements') or not db_user.user_details.body_measurements:
                    # Create new BodyMeasurementsModel
                    body_measurements = BodyMeasurementsModel(
                        user_details_id=db_user.user_details.id,
                        **user_update.user_details.body_measurements.dict()
                    )
                    db.add(body_measurements)
                else:
                    # Update existing BodyMeasurementsModel
                    for key, value in user_update.user_details.body_measurements.dict().items():
                        setattr(db_user.user_details.body_measurements, key, value)

            # Handle StylePreferencesModel
            if user_update.user_details.style_preferences:
                style_prefs = user_update.user_details.style_preferences
                if not hasattr(db_user.user_details, 'style_preferences') or not db_user.user_details.style_preferences:
                    # Create new StylePreferencesModel
                    new_style_prefs = StylePreferencesModel(
                        user_details_id=db_user.user_details.id,
                        favorite_colors=style_prefs.favorite_colors,
                        preferred_brands=style_prefs.preferred_brands,
                        lifestyle_choices=style_prefs.lifestyle_choices
                    )
                    db.add(new_style_prefs)
                    db.flush()

                    # Create BudgetModel
                    budget = BudgetModel(
                        style_preferences_id=new_style_prefs.id,
                        min_amount=style_prefs.budget.min_amount,
                        max_amount=style_prefs.budget.max_amount
                    )
                    db.add(budget)

                    # Create ShoppingHabits
                    shopping_habits = ShoppingHabitsModel(
                        style_preferences_id=new_style_prefs.id,
                        frequency=style_prefs.shopping_habits.frequency,
                        preferred_retailers=style_prefs.shopping_habits.preferred_retailers
                    )
                    db.add(shopping_habits)
                else:
                    # Update existing StylePreferencesModel
                    existing_style_prefs = db_user.user_details.style_preferences
                    for key, value in style_prefs.dict(exclude={'budget', 'shopping_habits'}).items():
                        setattr(existing_style_prefs, key, value)

                    # Update BudgetModel
                    if existing_style_prefs.budget:
                        for key, value in style_prefs.budget.dict().items():
                            setattr(existing_style_prefs.budget, key, value)
                    else:
                        budget = BudgetModel(
                            style_preferences_id=existing_style_prefs.id,
                            min_amount=style_prefs.budget.min_amount,
                            max_amount=style_prefs.budget.max_amount
                        )
                        db.add(budget)

                    # Update ShoppingHabits
                    if existing_style_prefs.shopping_habits:
                        for key, value in style_prefs.shopping_habits.dict().items():
                            setattr(existing_style_prefs.shopping_habits, key, value)
                    else:
                        shopping_habits = ShoppingHabitsModel(
                            style_preferences_id=existing_style_prefs.id,
                            frequency=style_prefs.shopping_habits.frequency,
                            preferred_retailers=style_prefs.shopping_habits.preferred_retailers
                        )
                        db.add(shopping_habits)

        # Update UserPreferences
        if user_update.user_preferences:
            if not db_user.user_preferences:
                user_preferences = UserPreferencesModel(
                    user_id=user_id,
                    **user_update.user_preferences.dict()
                )
                db.add(user_preferences)
            else:
                for key, value in user_update.user_preferences.dict().items():
                    setattr(db_user.user_preferences, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    except Exception as e:
        db.rollback()
        raise e