from sqlalchemy import Column, BigInteger, String, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Household(Base):
    __tablename__ = "households"

    household_id = Column(BigInteger, primary_key=True)
    neighborhood_id = Column(
        BigInteger,
        ForeignKey("neighborhoods.neighborhood_id")
    )
    route_id = Column(
        BigInteger,
        ForeignKey("routes.route_id")
    )
    house_number = Column(String(30))
    street = Column(String(100))
    monthly_fee = Column(Numeric(10, 2))
    collection_preference = Column(String(30))
    service_status = Column(String(20))