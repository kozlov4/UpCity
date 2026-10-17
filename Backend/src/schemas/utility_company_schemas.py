from pydantic import BaseModel, EmailStr
from typing import Optional, Annotated
from annotated_types import MinLen, MaxLen

class AddUtilityCompany(BaseModel):
    name: Annotated[str, MinLen(3), MaxLen(35)]
    address:Annotated[str, MinLen(10), MaxLen(150)]
    phone: Annotated[str, MinLen(10), MaxLen(20)]
    email: EmailStr
    password: Annotated[str, MinLen(8), MaxLen(64)]
  
class UtilityCompanyUpdate(BaseModel):
    name: Annotated[str, MinLen(3), MaxLen(35)]
    address:Annotated[str, MinLen(10), MaxLen(150)]
    phone: Annotated[str, MinLen(10), MaxLen(20)]
    email: EmailStr
    
  
class ShowUtilityCompany(BaseModel):
    ut_company_id: int
    name:str
    address:str
    phone:str
    rating: Optional[int] = 0
    
    model_config = {
        "from_attributes": True
    }

class ShowOneUtilityCompany(BaseModel):
    ut_company_id: int
    name:str
    address:str
    phone:str
    email:EmailStr


class ShowUtilityCompanyID(BaseModel):
    name:str

    model_config = {
        "from_attributes": True
    }

class LoginAdminCompanyUser(BaseModel):
    email: EmailStr
    password: str