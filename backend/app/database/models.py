from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Numeric,
    ForeignKey,
    Boolean,
    Date,
    Time,
    DateTime,
    Text,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Household(Base):
    __tablename__ = "households"

    household_id = Column(BigInteger, primary_key=True)

    neighborhood_id = Column(
        BigInteger,
        ForeignKey("neighborhoods.neighborhood_id"),
    )

    route_id = Column(
        BigInteger,
        ForeignKey("routes.route_id"),
    )

    house_number = Column(String(30))
    street = Column(String(100))
    monthly_fee = Column(Numeric(10, 2))
    collection_preference = Column(String(30))
    service_status = Column(String(20))


class Resident(Base):
    __tablename__ = "residents"

    resident_id = Column(BigInteger, primary_key=True)

    household_id = Column(
        BigInteger,
        ForeignKey("households.household_id"),
    )

    full_name = Column(String(150))
    phone_number = Column(String(30))
    is_primary_contact = Column(Boolean)
    status = Column(String(20))


class Worker(Base):
    __tablename__ = "workers"

    worker_id = Column(BigInteger, primary_key=True)

    full_name = Column(String(150))
    phone_number = Column(String(30))
    role = Column(String(30))
    status = Column(String(20))


class Route(Base):
    __tablename__ = "routes"

    route_id = Column(BigInteger, primary_key=True)

    neighborhood_id = Column(
        BigInteger,
        ForeignKey("neighborhoods.neighborhood_id"),
    )

    route_name = Column(String(100))
    description = Column(Text)
    status = Column(String(20))


class CollectionAssignment(Base):
    __tablename__ = "collection_assignments"

    assignment_id = Column(BigInteger, primary_key=True)

    worker_id = Column(
        BigInteger,
        ForeignKey("workers.worker_id"),
    )

    route_id = Column(
        BigInteger,
        ForeignKey("routes.route_id"),
    )

    assignment_date = Column(Date)
    status = Column(String(20))


class CollectionSchedule(Base):
    __tablename__ = "collection_schedules"

    schedule_id = Column(BigInteger, primary_key=True)

    route_id = Column(
        BigInteger,
        ForeignKey("routes.route_id"),
    )

    assignment_id = Column(
        BigInteger,
        ForeignKey("collection_assignments.assignment_id"),
    )

    scheduled_date = Column(Date)
    scheduled_time = Column(Time)
    status = Column(String(20))


class CollectionRecord(Base):
    __tablename__ = "collection_records"

    collection_record_id = Column(BigInteger, primary_key=True)

    schedule_id = Column(
        BigInteger,
        ForeignKey("collection_schedules.schedule_id"),
    )

    household_id = Column(
        BigInteger,
        ForeignKey("households.household_id"),
    )

    status = Column(String(20))
    missed_reason = Column(String(100))
    company_responsible = Column(Boolean)
    rescheduled_date = Column(Date)
    notes = Column(Text)
    recorded_at = Column(DateTime(timezone=True))


class BillingRecord(Base):
    __tablename__ = "billing_records"

    billing_id = Column(BigInteger, primary_key=True)

    household_id = Column(
        BigInteger,
        ForeignKey("households.household_id"),
    )

    billing_period = Column(Date)
    amount_due = Column(Numeric(10, 2))
    due_date = Column(Date)
    status = Column(String(20))


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(BigInteger, primary_key=True)

    household_id = Column(
        BigInteger,
        ForeignKey("households.household_id"),
    )

    amount = Column(Numeric(10, 2))
    payment_date = Column(Date)
    payment_method = Column(String(30))
    transaction_reference = Column(String(100))
    received_by = Column(
        BigInteger,
        ForeignKey("workers.worker_id"),
    )
    receipt_number = Column(String(50))
    status = Column(String(20))


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    payment_id = Column(
        BigInteger,
        ForeignKey("payments.payment_id"),
        primary_key=True,
    )

    billing_id = Column(
        BigInteger,
        ForeignKey("billing_records.billing_id"),
        primary_key=True,
    )

    amount_allocated = Column(Numeric(10, 2))