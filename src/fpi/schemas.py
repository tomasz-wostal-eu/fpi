from pydantic import BaseModel, ConfigDict

class PlantBase(BaseModel):
    name: str
    latin_name: str

class PlantCreate(PlantBase):
    pass

class PlantUpdate(BaseModel):
    name: str | None = None  # Fields can be optional for updates
    latin_name: str | None = None

    model_config = ConfigDict(from_attributes=True)

class Plant(PlantBase):
    id: int

    model_config = ConfigDict(from_attributes=True)