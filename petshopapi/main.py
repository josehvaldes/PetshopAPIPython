from contextlib import asynccontextmanager
from fastapi import FastAPI
 #import user_router
from petshopapi import item_routes, user_routes, sales_routes
from petshopapi.logger_config import logger
from petshopapi.config import settings

initializer: str = None

# Define a lifespan context manager to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    logger.info(f"Starting up PetShopAPI. version: {settings["version"]}")
    global initializer 
    initializer = "ML model loaded"  # Placeholder for actual model loading logic
    yield
    # Clean up the ML models and release the resources
    logger.info("PetShop API Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    global initializer 
    return {"status": f"{initializer}" }

app.include_router(item_routes.router, prefix="/items", tags=["items"])
app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(sales_routes.router, prefix="/sales", tags=["sales"])

