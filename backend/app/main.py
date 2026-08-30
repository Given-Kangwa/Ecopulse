from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.routes.households import router as household_router


app = FastAPI(
    title="EcoPulse API",
    description="Backend API for the EcoPulse waste collection management system",
    version="1.0.0"
)


app.include_router(household_router)


@app.get("/")
def root():
    return {
        "message": "EcoPulse API is running",
        "version": "1.0.0"
    }


@app.get("/db-test")
def database_test():
    db: Session = SessionLocal()

    try:
        result = db.execute(text("SELECT current_database();"))
        database_name = result.scalar()

        return {
            "database_connected": True,
            "database": database_name
        }

    except Exception as e:
        return {
            "database_connected": False,
            "error": str(e)
        }

    finally:
        db.close()