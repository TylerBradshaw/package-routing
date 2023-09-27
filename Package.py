class Package:
    """
    Represents a package with details about its address, deadline, weight, and delivery status.
    """
    def __init__(self, id, address, city, state, zipcode, deadline, weight, status):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.weight = weight
        self.status = status
        self.departure_time = None
        self.delivery_time = None
        self.truck = None

    def __str__(self):
        return (
            f"ID: {self.id}\n"
            f"Address: {self.address}\n"
            f"City: {self.city}\n"
            f"State: {self.state}\n"
            f"Zipcode: {self.zipcode}\n"
            f"Deadline: {self.deadline}\n"
            f"Weight: {self.weight} Kg\n"
            f"Status: {self.status}\n"
            f"On Truck: {self.truck}\n"
        )

    def update_status(self, user_selected_time):
        if self.delivery_time < user_selected_time:
            self.status = f"Delivered @ {self.delivery_time}"
        elif self.departure_time > user_selected_time:
            self.status = "At Hub"
        else:
            self.status = "En route"
