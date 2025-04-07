from datetime import datetime


class PTRFiling:
    def __init__(self, rep_name: str, ptr_id: int, filing_date: datetime):
        self.representative: str = rep_name
        self.id: int = ptr_id
        self.date: datetime = filing_date

    def __repr__(self):
        return f'{self.id} :: {self.representative} :: {self.date}'
