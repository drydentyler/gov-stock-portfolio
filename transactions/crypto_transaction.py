from .transaction import Transaction


class Cryptocurrency(Transaction):
    def __init__(self, transaction_tuple, **kwargs):
        super().__init__(*transaction_tuple)
        self.nickname = None if 'nickname' not in kwargs else kwargs['nickname']
        if 'asset_name' in kwargs and kwargs['asset_name'] is not None:
            self.asset_name = kwargs['asset_name']
        else:
            self.asset_name = self.nickname

    def __repr__(self):
        return f'{self.ex_date}~{self.asset_type}~{self.type}~{self.asset_name}~{self.nickname}~{self.minimum}~{self.maximum}'
