from sqlalchemy.orm import Session
from ..models.models import User, UserDetails, BodyMeasurements, StylePreferences, Budget, ShoppingHabits, UserPreferences
from ..schemas.schemas import UserCreate, UserUpdate
from ..auth.jwt_handler import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    try:
        # Update UserDetails
        if user_update.user_details:
            if not db_user.user_details:
                # Create new UserDetails if it doesn't exist
                user_details = UserDetails(
                    user_id=user_id,
                    **user_update.user_details.dict(exclude={'body_measurements', 'style_preferences'})
                )
                db.add(user_details)
                db.flush()  # Flush to get the user_details.id
            else:
                # Update existing UserDetails
                for key, value in user_update.user_details.dict(exclude={'body_measurements', 'style_preferences'}).items():
                    setattr(db_user.user_details, key, value)

            # Ensure user_details is attached to db_user
            if not db_user.user_details:
                db.refresh(db_user)

            # Handle BodyMeasurements
            if user_update.user_details.body_measurements:
                if not hasattr(db_user.user_details, 'body_measurements') or not db_user.user_details.body_measurements:
                    # Create new BodyMeasurements
                    body_measurements = BodyMeasurements(
                        user_details_id=db_user.user_details.id,
                        **user_update.user_details.body_measurements.dict()
                    )
                    db.add(body_measurements)
                else:
                    # Update existing BodyMeasurements
                    for key, value in user_update.user_details.body_measurements.dict().items():
                        setattr(db_user.user_details.body_measurements, key, value)

            # Handle StylePreferences
            if user_update.user_details.style_preferences:
                style_prefs = user_update.user_details.style_preferences
                if not hasattr(db_user.user_details, 'style_preferences') or not db_user.user_details.style_preferences:
                    # Create new StylePreferences
                    new_style_prefs = StylePreferences(
                        user_details_id=db_user.user_details.id,
                        favorite_colors=style_prefs.favorite_colors,
                        preferred_brands=style_prefs.preferred_brands,
                        lifestyle_choices=style_prefs.lifestyle_choices
                    )
                    db.add(new_style_prefs)
                    db.flush()

                    # Create Budget
                    budget = Budget(
                        style_preferences_id=new_style_prefs.id,
                        min_amount=style_prefs.budget.min_amount,
                        max_amount=style_prefs.budget.max_amount
                    )
                    db.add(budget)

                    # Create ShoppingHabits
                    shopping_habits = ShoppingHabits(
                        style_preferences_id=new_style_prefs.id,
                        frequency=style_prefs.shopping_habits.frequency,
                        preferred_retailers=style_prefs.shopping_habits.preferred_retailers
                    )
                    db.add(shopping_habits)
                else:
                    # Update existing StylePreferences
                    existing_style_prefs = db_user.user_details.style_preferences
                    for key, value in style_prefs.dict(exclude={'budget', 'shopping_habits'}).items():
                        setattr(existing_style_prefs, key, value)

                    # Update Budget
                    if existing_style_prefs.budget:
                        for key, value in style_prefs.budget.dict().items():
                            setattr(existing_style_prefs.budget, key, value)
                    else:
                        budget = Budget(
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
                        shopping_habits = ShoppingHabits(
                            style_preferences_id=existing_style_prefs.id,
                            frequency=style_prefs.shopping_habits.frequency,
                            preferred_retailers=style_prefs.shopping_habits.preferred_retailers
                        )
                        db.add(shopping_habits)

        # Update UserPreferences
        if user_update.user_preferences:
            if not db_user.user_preferences:
                user_preferences = UserPreferences(
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