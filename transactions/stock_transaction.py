from .transaction import Transaction


class Stocks(Transaction):
    def __init__(self, transaction_tuple, **kwargs):
        super().__init__(*transaction_tuple)
        self.ticker = None if 'ticker' not in kwargs else kwargs['ticker']
        self.asset_name = None if 'asset_name' not in kwargs else kwargs['asset_name']

    def __repr__(self):
        return f'{self.ex_date}~{self.asset_type}~{self.type}~{self.asset_name}~{self.ticker}~{self.minimum}~{self.maximum}'

    def __str__(self):
        return f'{"Bought" if self.type == "P" else "Sold" if self.type == "S" else self.type}: {self.asset_type} ' \
               f'{self.asset_name if self.ticker is None else self.ticker} between {self.minimum}-{self.maximum}'
