from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="UpCity 🌇",
    description="API для роботи з комунальними підприємствами, платежами, користувачами та іншим.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/images", StaticFiles(directory="/var/www/myapp/uploads/images"), name="images"
)
