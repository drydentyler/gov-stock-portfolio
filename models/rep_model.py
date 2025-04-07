"""
Representatives Table Layout:
id          int         primary key -> ptr_filings.rep_id
name        str
"""


class RepresentativesModel:
    def __init__(self, connection):
        self.conn = connection
        self.cursor = self.conn.cursor()

    def get_representatives(self) -> [(int, str)]:
        """
        Get list of tuples for all representative records

        Returns:
            [(int, str)]: tuple values where int is rep id and str is rep name
        """
        try:
            self.cursor.execute("SELECT * FROM representatives")
            return [item for item in self.cursor.fetchall()]
        except Exception as e:
            print(f'Error occurred getting all representatives: {e}')
            return []

    def get_representative(self, name: str = None, rep_id: int = None) -> (int, str):
        """
        Get a representative given either name or id

        Args:
            name: str, name of representative
            rep_id: int, id value of representative

        Returns:
            (int, str): tuple for representative information
        """
        if not name and not rep_id:
            print(f'Could not get representative, no name/rep_id provided.')
            return -1, ''

        if rep_id:
            return self._get_rep_by_id(rep_id)
        else:
            return self._get_rep_by_name(name)

    def _get_rep_by_id(self, rep_id: int) -> (int, str):
        """
        Get a representative by rep_id

        Args:
            rep_id: int, representative id

        Returns:
            (int, str), tuple where int is rep id and str is rep name
        """
        try:
            self.cursor.execute("SELECT * from representatives WHERE id = ?", (rep_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f'Error occurred getting representative by id {rep_id}: {e}')
            return -1, ''

    def _get_rep_by_name(self, name: str) -> (int, str):
        """
        Get representative information by name

        Args:
            name: str, representative name

        Returns:
            (int, str), int is rep id and str is rep name
        """
        try:
            self.cursor.execute("SELECT * from representatives WHERE name = ?", (name,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f'Error occurred getting representative by name {name}: {e}')
            return -1, ''

    def insert_rep(self, rep: list[str] | str):
        """
        Insert a representative given a name or list of names

        Args:
            rep: str or [str], single or list of representative names
        """
        try:
            # Check if the input is a list, if so, pass to insert rep batch, otherwise to insert single rep
            if isinstance(rep, list):
                self.insert_rep_batch(rep)
            else:
                return self.insert_rep_single(rep)
        except Exception as e:
            print(f'Error occurred inserting rep(s) {rep}: {e}')

    def insert_rep_batch(self, names: [str]):
        """
        Insert multiple representatives in a single call

        Args:
            names: [str], list of strings for rep names
        """
        try:
            # Ensure that names has values in it
            if names:
                # If there's one value in list of names, create single tuple, otherwise create list of tuples as params
                name_params = (names[0],) if len(names) == 1 else [(name,) for name in names]

                # Set execute to either cursor.execute or .executemany depending on list of params
                execute = self.cursor.execute if len(name_params) == 1 else self.cursor.executemany

                insert_str = "INSERT INTO representatives (name) VALUES(?)"
                execute(insert_str, name_params)
                self.conn.commit()
        except Exception as e:
            print(f'Error occurred while inserting rep batch: {e}')

    def insert_rep_single(self, name: str) -> int:
        """
        Insert a single representative by name and return the newly assigned integer value of their ID

        Args:
            name: str, representative name

        Returns:
            int, newly assigned Rep ID
        """
        try:
            # Check if the representative already exists, -1 returns if an error occurs getting them, None if not found
            exists = self.get_representative(name)
            # Don't want to re-insert if an error occurred searching for them, handle that separately
            if exists is None:
                insert_str = "INSERT INTO representatives (name) VALUES(?)"
                self.cursor.execute(insert_str, (name,))
                self.conn.commit()
                # Return the id by searching for the rep in the database again
                return self.get_representative(name=name)[0]
            else:
                return exists[0]
        except Exception as e:
            print(f'Error occurred while inserting rep {name}: {e}')
            return -1
