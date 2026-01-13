from pydantic import BaseModel, Field, ConfigDict

class VoziloCreate(BaseModel):
    marka: str = Field(min_length=2)
    model: str = Field(min_length=1)
    godiste: int = Field(ge=1950, le=2100)
    tablice: str = Field(min_length=5, max_length=12)

class VoziloUpdate(BaseModel):
    marka: str = Field(min_length=2)
    model: str = Field(min_length=1)
    godiste: int = Field(ge=1950, le=2100)
    tablice: str = Field(min_length=5, max_length=12)

class VoziloOut(BaseModel):
    id: int
    marka: str
    model: str
    godiste: int
    tablice: str

    model_config = ConfigDict(from_attributes=True)
