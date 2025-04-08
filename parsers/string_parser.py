import re
from datetime import datetime

# The problem with this pattern is that it is looking for any sort of non word character including ()
# TYPE_PATTERN = r'\W\w{2}\W'
# Search for square brackets with 2 characters inside, indicating the asset type
TYPE_PATTERN = r'\[\w{2}\]'

# Search for 1-3 digits following a '$' and followed by either a ',' or '.'
AMOUNT_PATTERN = r'\$\d{1,3}[\,,.]'

# Search for two digits+'/'+two digits+'/'+four digits+two digits+'/'+two digits+'/'+four digits
DATE_PATTERN = r"\d{2}\/\d{2}\/\d{4}\d{2}\/\d{2}\/\d{4}"

# Search for '(' some word characters and ')'
NICKNAME_PATTERN = r"\(\w+\)"

# Search for D followed by 10 \\x00 and ': ', this is the description field
DESCRIPTION_PATTERN = r"D"+('\\x00'*10)+': '

# Search for C followed by 7 \\x00 and ': ', this is the comment field
COMMENT_PATTERN = f"C"+('\\x00'*7)+': '

# Search for at least 1 word character followed by at most 1 non-word character and then at most 1 word character,
# all contained within parentheses, this will search for standard tickers (GOOG) and subclass tickers (BRK.B)
TICKER_PATTERN = r"\(\w{1,}\W{,1}\w{,1}\)"


class StringParser:
    # Class attribute that will be continuously altered to extract necessary information
    _tran_str: str

    @classmethod
    def parse_transaction_string(cls, asset_type: str, transaction_str: str, ptr_id: int):
        """
        Given a string of transaction information, parse it to return a tuple of the necessary information

        Args:
            asset_type: str, the asset type of the transaction
            transaction_str: str, the full transaction string with the asset type not extracted
            ptr_id: int, the PTR Filing ID that the transaction has come from

        Returns:
            tuple of the necessary information to build a transaction object
        """
        # Set the class attribute to the provided transaction string
        cls._tran_str = transaction_str

        # The ordering is important for pulling the information, owner is the first 2 characters of the string
        owner = cls._get_owner()
        # Transaction type is either [P, S, E] followed by a space
        transaction_type = cls._get_purchase_sale()
        # Extract and remove the dates that go together in the format ??/??/??????/??/????
        ex_date, notified = cls._get_dates()
        # Search for the first dollar value as the minimum
        minimum = cls._get_minimum()
        # Search for second as the maximum
        maximum = cls._get_maximum()
        if maximum is None:
            maximum = minimum

        # Get the class name by searching for the asset type which is in []
        asset_name = cls._get_asset_name()

        # Options and Crypto will need to further extract information from the transaction string-> description/nickname
        if asset_type not in ['OP', 'CT']:
            cls._tran_str = ''

        return asset_type, ptr_id, owner, asset_name, transaction_type, minimum, maximum, ex_date, notified

    @staticmethod
    def get_asset_type(transaction_str: str) -> str:
        """
        Get the asset type located in [] from the transaction string

        Args:
            transaction_str: str, the full transaction string compiled from the pdf file

        Returns:
            str, the asset type of the transaction
        """
        try:
            match = re.search(TYPE_PATTERN, transaction_str)
            if match:
                asset_type = transaction_str[match.span()[0] + 1:match.span()[1] - 1]
                return asset_type
        except Exception as e:
            raise Exception(f'Something went wrong getting asset type code for transaction: {e}')

    @classmethod
    def _get_owner(cls) -> str | None:
        """
        Get the owner from the class attribute transaction string

        Returns:
            str or None, owner if it can be found in the string
        """
        try:
            # These are the owners that have come across from all the filings
            for owner in ['SP ', 'DC ', 'JT ']:
                # try to find an index of these owner codes in the transaction string
                start_index = cls._tran_str.find(owner)
                if start_index != -1:
                    owner_id = cls._tran_str[start_index:start_index+2]
                    # Remove the first two characters from the string if they are the owner code
                    cls._tran_str = cls._tran_str[start_index+2:].strip()
                    return owner_id
            return None
        except Exception as e:
            raise Exception(f'Something went wrong getting owner for transaction: {e}')

    @classmethod
    def _get_asset_name(cls) -> str | None:
        """
        Get the asset name from the class attribute transaction string

        Returns:
            str or None, value of asset name
        """
        # Regex search for the asset type in square brackets, the name is the portion of the string preceding it
        match = re.search(TYPE_PATTERN, cls._tran_str)
        if match:
            # Remove any trailing white space and any excess spaces in the name
            name = re.sub(r"\s+", " ", cls._tran_str[:match.span()[0]].strip())
            cls._clean_transaction_str(name)
            return name
        return None

    @classmethod
    def _get_purchase_sale(cls) -> str:
        """
        Get the transaction type, whether it was a Purchase (P) or Sell (S) or E(?)

        Return:
            str, character indicating the type of transaction
        """
        try:
            # P - Purchase, S - Sale, E - Exchange
            for action in ['P ', 'S ', 'E ']:
                # Search for the characters indicating the transaction type in the string until one is found
                found = cls._tran_str.find(action)
                if found != -1:
                    t_type = cls._tran_str[found]
                    cls._clean_transaction_str(action)
                    return t_type
        except Exception as e:
            raise Exception(f'Something went wrong getting purchase/sale for transaction: {e}')

    @classmethod
    def _get_minimum(cls) -> int:
        """
        Get the minimum of the transaction value range from the class attribute transaction string

        Return:
            int, minimum of the range for the transaction
        """
        try:
            # Regex search for the amount pattern in the transaction string
            match = re.search(AMOUNT_PATTERN, cls._tran_str)
            unit_start = match.start()
            space_index = cls._tran_str[unit_start:].index(' ')
            amount_str = cls._tran_str[unit_start:space_index+unit_start]
            cls._clean_transaction_str(amount_str)

            # Had to add in an additional cast to a float first incase a decimal is encountered like $800.00
            return int(float(amount_str[1:].replace(',', '')))
        except Exception as e:
            raise Exception(f'Something went wrong getting minimum for transaction: {e}')

    @classmethod
    def _get_maximum(cls) -> int | None:
        """
        Get the maximum for the value of the class attribute transaction string

        Returns:
            int or None, value of the maximum dollar amount for the transaction if it can be found
        """
        try:
            # Search the transaction string for the amount regex pattern
            match = re.search(AMOUNT_PATTERN, cls._tran_str)
            if match:
                unit_start = match.start()

                # From the start of regex match, search for a ' '
                end_index = cls._tran_str[unit_start:].find(' ')

                # If there is a space, set the amount equal to the start of the regex match to the end index
                if end_index != -1:
                    amount = cls._tran_str[unit_start:unit_start+end_index]
                # Otherwise set amount equal to the regex match to the end
                else:
                    amount = cls._tran_str[unit_start:]

                # Remove the amount from the transaction string
                cls._clean_transaction_str(amount)

                # Return the amount, skipping the $, and removing any commas
                # Had to add in an additional cast to a float first incase a decimal is encountered like $800.00
                return int(float(amount[1:].replace(',', '')))
            return None
        except Exception as e:
            raise Exception(f'Something went wrong getting maximum for transaction: {e}')

    @classmethod
    def _get_dates(cls) -> (datetime, datetime):
        """
        Get the executed and notified date from the class attribute transaction string

        Returns:
            tuple(datetime, datetime), first item is the executed date and second is the date notified
        """
        try:
            # Regex search for the date pattern in the transaction string
            match = re.search(DATE_PATTERN, cls._tran_str)
            if match:
                dates_str = cls._tran_str[match.span()[0]:match.span()[1]]

                first_date = datetime.strptime(dates_str[:10], "%m/%d/%Y")
                second_date = datetime.strptime(dates_str[10:], "%m/%d/%Y")

                cls._clean_transaction_str(dates_str)
                return first_date, second_date
        except Exception as e:
            raise Exception(f'Something went wrong getting dates for transaction {cls._tran_str}: {e}')

    @classmethod
    def get_op_description(cls) -> str | None:
        """
        Get the description for any Options transaction, describing what the option was

        Returns:
            str or None, description for the Option transaction if it can be found
        """
        try:
            # Regex search for the description and comment pattern in the transaction string
            desc_match = re.search(DESCRIPTION_PATTERN, cls._tran_str)
            com_match = re.search(COMMENT_PATTERN, cls._tran_str)
            if desc_match:
                start_index = desc_match.span()[1]
                # If there is also a comment, the description will end at the beginning of the comments
                if com_match:
                    end_index = com_match.span()[0]
                    desc = cls._tran_str[start_index:end_index]
                # If there isn't a comment then the description is the last field of the transaction
                else:
                    desc = cls._tran_str[start_index:]
                cls._tran_str = ''
                return desc.strip()
        except Exception as e:
            print(f'Error occurred while getting the description for an Option transaction: {e}')

        cls._tran_str = ''
        return None

    @staticmethod
    def get_stock_name(asset_name: str) -> (str, str):
        """
        Get the ticker/nickname from a given asset name

        Args:
            asset_name: str, the asset name to extract a ticker/nickname from

        Returns:
            tuple(str, str), first item is the ticker/nickname and second is the asset name
        """
        # Regex search for the ticker pattern in the asset name
        ticker_match = re.search(TICKER_PATTERN, asset_name)
        if ticker_match:
            # Separate out the name and ticker from the asset_name string
            name = asset_name[:ticker_match.span()[0]].strip()
            ticker = asset_name[ticker_match.span()[0] + 1:ticker_match.span()[1] - 1]

            return ticker, name
        # Return None for ticker if the pattern wasn't found in the asset name string
        return None, asset_name

    @classmethod
    def _clean_transaction_str(cls, replace: str):
        """
        Remove a given string in the class attribute transaction string, and remove any excess spaces

        Args:
            replace: str, the string to be removed from the transaction string
        """
        # Remove the given string from the transaction string
        cls._tran_str = cls._tran_str.replace(replace, '').strip()

        # Replace any excess spaces in the transaction string with single spaces
        cls._tran_str = re.sub(r"\s", " ", cls._tran_str)

