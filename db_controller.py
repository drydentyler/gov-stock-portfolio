from models import *
import sqlite3


class DBController:
    def __init__(self):
        self.conn = sqlite3.connect('gov_stock_portfolio.db')
        self.rep_model = RepresentativesModel(self.conn)
        self.ptr_model = PTRFilingModel(self.conn)
        self.tran_model = TransactionModel(self.conn)

    def close(self):
        self.conn.close()
