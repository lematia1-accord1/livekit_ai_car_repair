import enum
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"

class AssistantFnc:
    """Plain Python class with car functions"""
    def __init__(self):
        self._car_details = {
            CarDetails.VIN: "",
            CarDetails.Make: "",
            CarDetails.Model: "",
            CarDetails.Year: ""
        }

    def get_car_str(self):
        return "\n".join(f"{key.value}: {value}" for key, value in self._car_details.items())

    # Regular methods (no decorator)
    def lookup_car(self, vin: str):
        logger.info("lookup car - vin: %s", vin)
        result = DB.get_car_by_vin(vin)
        if not result:
            return "Car not found"
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        return f"The car details are:\n{self.get_car_str()}"

    def get_car_details(self):
        logger.info("get car details")
        return f"The car details are:\n{self.get_car_str()}"

    def create_car(self, vin: str, make: str, model: str, year: int):
        logger.info("create car - vin: %s, make: %s, model: %s, year: %s", vin, make, model, year)
        result = DB.create_car(vin, make, model, year)
        if not result:
            return "Failed to create car"
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        return "Car created!"

    def has_car(self):
        return self._car_details[CarDetails.VIN] != ""
