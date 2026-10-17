from pydantic import BaseModel

class ImageOut(BaseModel):
    image_id: int
    image_url: str

    model_config = {
        "from_attributes": True
    }