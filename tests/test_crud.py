import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fpi.models import Base, Plant
from fpi.crud import get_items, create_item, update_item, delete_item, get_item_by_id
from fpi.schemas import PlantCreate, PlantUpdate

# Set the DATABASE_URL for tests
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    # Create the database and the tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_plant(db):
    plant = PlantCreate(name="Rose", latin_name="Rosa")
    created_plant = create_item(plant, db)
    assert created_plant.name == "Rose"
    assert created_plant.latin_name == "Rosa"

def test_get_items(db):
    plants = get_items(db=db)
    assert len(plants) == 0

def test_update_plant(db):
    # First create a plant
    plant = PlantCreate(name="Sunflower", latin_name="Helianthus")
    created_plant = create_item(plant, db)

    # Now update the plant
    update_data = PlantUpdate(name="Updated Sunflower", latin_name="Updated Helianthus")
    updated_plant = update_item(created_plant.id, update_data, db)

    assert updated_plant.name == "Updated Sunflower"
    assert updated_plant.latin_name == "Updated Helianthus"

def test_delete_plant(db):
    # First create a plant
    plant = PlantCreate(name="Tulip", latin_name="Tulipa")
    created_plant = create_item(plant, db)

    # Now delete the plant
    deleted_plant = delete_item(created_plant.id, db)
    assert deleted_plant is not None
    assert deleted_plant.name == "Tulip"

    # Check that the plant no longer exists
    fetched_plant = get_item_by_id(created_plant.id, db)
    assert fetched_plant is None

def test_delete_non_existent_plant(db):
    # Try to delete a non-existent plant
    deleted_plant = delete_item(item_id=9999, db=db)
    
    # Should return None since the plant doesn't exist
    assert deleted_plant is None

def test_update_non_existent_plant(db):
    # Try to update a non-existent plant
    update_data = PlantUpdate(name="Non-existent Plant", latin_name="Non-existent LatinName")
    updated_plant = update_item(item_id=9999, plant=update_data, db=db)
    
    # Should return None since the plant doesn't exist
    assert updated_plant is None
