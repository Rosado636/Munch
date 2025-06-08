from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import the startup function to create tables
from .db import create_db_and_tables

# Import the restaurant route handlers
from .routes import restaurants, reviews

# Define lifespan logic: runs once when app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  # Create DB tables at startup
    yield  # Nothing on shutdown for now

# Create the FastAPI app and register the lifespan
app = FastAPI(lifespan=lifespan)

# Register the /restaurants route group
app.include_router(restaurants.router)
app.include_router(reviews.router)
