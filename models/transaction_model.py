from transactions import *

"""
Transactions Table Layout:
transaction_id          int         primary key
ptr_id                  int         foreign key -> ptr_filings.ptr_id
asset_type              str         
owner                   str
asset_name              str
ticker                  str
description             str
nickname                str
type                    str
minimum                 int
maximum                 int
executed                datetime
notified                datetime
"""


class TransactionModel:
    def __init__(self, connection):
        self.conn = connection
        # This needs to be .cursor() because the return is a cursor object, otherwise it is just the function
        self.cursor = self.conn.cursor()

    def get_all_transactions(self) -> [Transaction]:
        """
        Get all transactions in the database

        Returns:
            [Transaction]: list of transactions from the database
        """
        try:
            self.cursor.execute('SELECT * FROM transactions')
            res = self.cursor.fetchall()
            transactions = [TransactionFactory.from_db_tuple(transaction) for transaction in res]
            return transactions
        except Exception as e:
            print(f'Error occurred getting all transactions: {e}')
            return []

    def get_transaction_by(self, **kwargs) -> [Transaction]:
        """
        Get all the transactions by a given keyword: asset_type, type, ex_date, notified

        Returns:
            [Transaction]: list of transactions for the given keyword argument
        """
        if 'asset_type' in kwargs:
            where_statement = "WHERE asset_type = ?"
            condition = (kwargs['asset_type'],)

        elif 'type' in kwargs:
            where_statement = "WHERE type = ?"
            condition = (kwargs['type'],)

        # TODO: This may end up being broken out into its own func to get within certain ranges?
        elif 'ex_date' in kwargs:
            where_statement = "WHERE executed <= ?"
            condition = (kwargs['ex_date'],)

        elif 'notified' in kwargs:
            where_statement = "WHERE notified <= ?"
            condition = (kwargs['notified'],)

        else:
            condition = None
            where_statement = ''

        if condition:
            try:
                select_statement = 'SELECT * FROM transactions ' + where_statement
                self.cursor.execute(select_statement, condition)

                res = self.cursor.fetchall()
                transactions = [TransactionFactory.from_db_tuple(transaction) for transaction in res]
                return transactions
            except Exception as e:
                print(f'Error occurred while getting transactions by {kwargs.items()}: {e}')
                return []
        else:
            return self.get_all_transactions()

    def insert_transaction(self, transaction: Transaction | list[Transaction]):
        """
        Insert a transaction or list of transactions

        Args:
            transaction: Transaction or [Transaction], single or batch of transaction objects
        """
        if isinstance(transaction, list):
            self.insert_transaction_batch(transaction)
        else:
            self.insert_transaction_single(transaction)

    def insert_transaction_batch(self, transactions: [Transaction]):
        """
        Insert a batch of transactions

        Args:
            transactions: [Transaction], list of transaction objects
        """
        try:
            if len(transactions) == 1:
                transaction_params = self._build_transaction_params(transactions[0])
            else:
                transaction_params = []
                for t in transactions:
                    if t is not None:
                        transaction_params.append(self._build_transaction_params(t))

            insert_str = "INSERT INTO transactions (ptr_id, " \
                         "asset_type, " \
                         "owner, " \
                         "asset_name, " \
                         "ticker, " \
                         "description, " \
                         "nickname, " \
                         "type, " \
                         "minimum, " \
                         "maximum, " \
                         "executed, " \
                         "notified) " \
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            # Set an execute variable based on if a single transaction made it through or if there are many
            execute = self.cursor.execute if len(transactions) == 1 else self.cursor.executemany
            execute(insert_str, transaction_params)
            self.conn.commit()
            # Connection close function is here because this is only called by the aggregator in its final step
            # Update 4/25/2025: the database controller updated to include __exit__ function that will close connection
            # self.conn.close()
        except Exception as e:
            print(f'Error occurred inserting transactions: {e}')

    def insert_transaction_single(self, transaction: Transaction):
        """
        Insert a single transaction

        Args:
            transaction: Transaction, transaction object to be inserted
        """
        try:
            insert_str = "INSERT INTO transactions (ptr_id, " \
                         "asset_type, " \
                         "owner, " \
                         "asset_name, " \
                         "ticker, " \
                         "description, " \
                         "nickname, " \
                         "type, " \
                         "minimum, " \
                         "maximum, " \
                         "executed, " \
                         "notified) " \
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = self._build_transaction_params(transaction)
            self.cursor.execute(insert_str, params)
            self.conn.commit()
        except Exception as e:
            print(f'Error occurred inserting transaction from {transaction.ptr_id}: {e}')

    @staticmethod
    def _build_transaction_params(t: Transaction):
        """
        Helper method for converting a transaction object into a tuple with the correct information drawn from it

        Args:
            t: Transaction, a transaction object that the information will be taken from to build the tuple

        Returns:
            tuple with length 12 of all the necessary data to insert the transaction
        """
        try:
            match t.asset_type:
                case 'ST':
                    return t.ptr_id, 'ST', t.owner, t.asset_name, t.ticker, None, None, t.type, t.minimum, t.maximum, t.ex_date, t.notified
                case 'CT':
                    return t.ptr_id, 'CT', t.owner, t.asset_name, None, None, t.nickname, t.type, t.minimum, t.maximum, t.ex_date, t.notified
                case 'OP':
                    return t.ptr_id, 'OP', t.owner, t.asset_name, t.ticker, t.description, None, t.type, t.minimum, t.maximum, t.ex_date, t.notified
                case _:
                    return t.ptr_id, t.asset_type, t.owner, t.asset_name, None, None, None, t.type, t.minimum, t.maximum, t.ex_date, t.notified
        except Exception as e:
            print(f"Error occurred creating the parameters to insert transaction from {t.ptr_id}: {e}")
            return None
