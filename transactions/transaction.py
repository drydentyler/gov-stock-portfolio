from datetime import datetime


class Transaction:
    def __init__(self, asset_type: str, ptr_id: int, owner: str, asset_name: str, type: str, minimum: int, maximum: int, executed: datetime, notified: datetime):
        self.asset_type = asset_type
        self.ptr_id = ptr_id
        self.owner = owner
        self.asset_name = asset_name
        self.type = type
        self.minimum = minimum
        self.maximum = maximum
        self.ex_date = executed
        self.notified = notified

    # This one will be used mainly for debugging purposes and utilizes ~ as the separating character
    def __repr__(self):
        return f'{self.ex_date}~{self.asset_type}~{self.type}~{self.asset_name}~~{self.minimum}~{self.maximum}'

    # This is meant to be more user-friendly and will be how the user sees it printed in the console
    def __str__(self):
        return f'{"Bought" if self.type == "P" else "Sold" if self.type == "S" else self.type}: {self.asset_type} between {self.minimum}-{self.maximum}'
