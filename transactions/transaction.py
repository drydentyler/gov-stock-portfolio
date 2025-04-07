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

    def __repr__(self):
        return f'{self.ex_date}~{self.asset_type}~{self.type}~{self.asset_name}~~{self.minimum}~{self.maximum}'
