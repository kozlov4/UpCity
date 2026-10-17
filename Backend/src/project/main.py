from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from project.api import utility_company, user, authentication ,application, notification


app = FastAPI(
    title="UpCity 🌇",
    description="API для роботи з комунальними підприємствами, платежами, користувачами та іншим.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="/var/www/myapp/uploads/images"), name="images")

app.include_router(utility_company.router)
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(application.router)
app.include_router(notification.router)




