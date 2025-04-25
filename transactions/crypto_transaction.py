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

    def __str__(self):
        return f'{"Bought" if self.type == "P" else "Sold" if self.type == "S" else self.type}: {self.asset_type} ' \
               f'{self.asset_name if self.nickname is None else self.nickname} between {self.minimum}-{self.maximum}'
