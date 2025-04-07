from .stock_transaction import Stocks


class Options(Stocks):
    def __init__(self, transaction_tuple, **kwargs):
        super().__init__(transaction_tuple, **kwargs)
        self.description = None if 'description' not in kwargs else kwargs['description']

    def __repr__(self):
        return f'{self.ex_date}~{self.asset_type}~{self.type}~{self.asset_name}~{self.ticker}~{self.minimum}~{self.maximum}~{self.description}'
