class Truck:
    """
    Represents a truck that can carry packages.
    """
    def __init__(self, capacity, speed, packages, mileage, address, depart_time):
        self.capacity = capacity
        self.speed = speed
        self.packages = packages
        self.mileage = mileage
        self.address = address
        self.depart_time = depart_time
        self.time = depart_time
