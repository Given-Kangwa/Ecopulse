from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.routes.households import router as household_router
from app.routes.payment import router as payment_router
from app.routes.billing import router as billing_router
from app.routes.collections import router as collection_router
from app.routes.workers import router as worker_router
from app.routes.routes import router as route_router
from app.routes.assignments import router as assignment_router
from app.routes.complaints import router as complaint_router
from app.routes.incidents import router as incident_router
from app.routes.dashboard import router as dashboard_router

app = FastAPI(
    title="EcoPulse API",
    description="Backend API for the EcoPulse waste collection management system",
    version="1.0.0"
)


app.include_router(household_router)
app.include_router(payment_router)
app.include_router(billing_router)
app.include_router(collection_router)
app.include_router(worker_router)
app.include_router(route_router)
app.include_router(assignment_router)
app.include_router(complaint_router)
app.include_router(incident_router)
app.include_router(dashboard_router)


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