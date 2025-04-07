from ptr_filing import PTRFiling
from datetime import datetime

"""
PTR Filing Table layout:
ptr_id          int         primary key -> transactions.ptr_id
rep_id          int         foreign key -> reps.id
date            datetime    
"""


class PTRFilingModel:
    def __init__(self, connection):
        self.conn = connection
        self.cursor = self.conn.cursor()

    def get_ptr_filing_by_id(self, ptr_id: int) -> PTRFiling | None:
        """
        Get a PTR filing by the filing id

        Args:
            ptr_id: int, integer value of the desired PTR filing

        Returns:
            PTRFiling or None, creates a PTRFiling object if the id is found otherwise None
        """
        try:
            self.cursor.execute("SELECT p.ptr_id, r.name, p.date "
                                "FROM ptr_filings as p "
                                "JOIN representatives as r on r.id = p.rep_id "
                                "WHERE ptr_id = ?", (ptr_id,))
            res = self.cursor.fetchone()
            filing = PTRFiling(rep_name=res[1], ptr_id=res[0], filing_date=res[2])
            return filing
        except Exception as e:
            print(f'Error occurred reading PTR Filing {ptr_id}: {e}')
            return None

    def get_ptr_filing_by_rep_id(self, rep_id: int) -> [PTRFiling]:
        try:
            # Important to keep spaces at the end of each line to keep the query properly spaced out
            self.cursor.execute("Select r.name, p.ptr_id, p.date "
                                "FROM ptr_filings as p "
                                "JOIN representatives as r on r.id = p.rep_id "
                                "WHERE rep_id = ? ", (rep_id,))
            return [PTRFiling(rep_name=item[0], ptr_id=item[1], filing_date=item[2]) for item in self.cursor.fetchall()]
        except Exception as e:
            print(f'Error occurred getting filings for Rep ID: {rep_id}: {e}')
            return []

    def get_all_filings(self) -> [PTRFiling]:
        """
        Get all PTR Filings currently in the PTRFiling table

        Returns:
            [PTRFiling], list of PTR Filing objects
        """
        try:
            self.cursor.execute("Select r.name, ptr_id, date "
                                "FROM ptr_filings as p "
                                "JOIN representatives as r on r.id = p.rep_id")
            return [PTRFiling(rep_name=item[0], ptr_id=item[1], filing_date=item[2]) for item in self.cursor.fetchall()]
        except Exception as e:
            print(f'Error occurred getting all PTR filings: {e}')
            return []

    def insert_ptr_filing(self, ptr_id: int, rep_id: int, filing_date: datetime) -> bool:
        """
        Insert into the PTR Filings table a new record

        Args:
            ptr_id: int, id of a new PTR filing
            rep_id: int, representative's id
            filing_date: date of PTR filing

        Returns:
            bool, True if successfully added, False if an error occurred
        """
        try:
            insert_str = "INSERT INTO ptr_filings (ptr_id, rep_id, date) VALUES (?, ?, ?)"
            self.cursor.execute(insert_str, (ptr_id, rep_id, filing_date))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error occurred inserting into the PTR Filings table filing {ptr_id}: {e}")
            return False
