from sqlalchemy.orm import Session
from . import models, schemas

# Get a list of items with optional pagination
def get_items(skip: int = 0, limit: int = 10, db: Session = None):
    return db.query(models.Plant).offset(skip).limit(limit).all()

# Get a single item by ID
def get_item_by_id(item_id: int, db: Session):
    return db.query(models.Plant).filter(models.Plant.id == item_id).first()

# Create a new item
def create_item(plant: schemas.PlantCreate, db: Session):
    db_plant = models.Plant(**plant.model_dump())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

# Update an existing item
def update_item(item_id: int, plant: schemas.PlantUpdate, db: Session):
    db_plant = db.query(models.Plant).filter(models.Plant.id == item_id).first()
    if db_plant is None:
        return None

    # Update fields with the new values from plant model
    update_data = plant.model_dump(exclude_unset=True)  # Only update provided fields
    for key, value in update_data.items():
        setattr(db_plant, key, value)
    
    db.commit()
    db.refresh(db_plant)
    return db_plant

# Delete an item by ID
def delete_item(item_id: int, db: Session):
    db_plant = db.query(models.Plant).filter(models.Plant.id == item_id).first()
    if db_plant is None:
        return None
    
    db.delete(db_plant)
    db.commit()
    return db_plant
