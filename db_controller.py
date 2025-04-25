from models import *
import sqlite3


class DBController:
    def __init__(self):
        self.conn = sqlite3.Connection
        self.rep_model: RepresentativesModel
        self.ptr_model: PTRFilingModel
        self.tran_model: TransactionModel

    def __enter__(self):
        self.conn = sqlite3.connect('gov_stock_portfolio.db')
        self.rep_model = RepresentativesModel(self.conn)
        self.ptr_model = PTRFilingModel(self.conn)
        self.tran_model = TransactionModel(self.conn)
        return self

    def __exit__(self, exceptype, excepvalue, traceback):
        self.conn.close()
        if exceptype:
            print(f'An exception forced the database connection to close: {exceptype}: {excepvalue}')
            # Return True if the exception will be handled here, otherwise it will continue up
            return False
