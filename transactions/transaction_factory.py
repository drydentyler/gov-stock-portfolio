from .transaction import Transaction
from .stock_transaction import Stocks
from .crypto_transaction import Cryptocurrency
from .options_transaction import Options
from parsers import get_asset_type, parse_string, get_stock_name, get_op_description

# These are all the transaction types that can pass through the transaction factory and get parsed
SUPPORTED_ASSETS = ['ST', 'CT', 'CS', 'GS', 'OT', 'PS', 'OP', 'OI', 'HN', 'OL']

# These are the transaction types that contain specialized information needing subclasses of Transactions
SPECIALIZED = {
    'ST': Stocks,
    'CT': Cryptocurrency,
    'OP': Options
}

# ALl the asset codes listed on the website, will be able to specify what specific transaction type isn't supported
ASSET_CODES = {
    "4K": "401K and Other Non-Federal Retirement Accounts",
    "5C": "529 College Savings Plan",
    "5F": "529 Portfolio",
    "5P": "529 Prepaid Tuition Plan",
    "AB": "Asset-Backed Securities",
    "BA": "Bank Accounts, Money Market Accounts and CDs",
    "BK": "Brokerage Accounts",
    "CO": "Collectibles",
    "CS": "Corporate Securities (Bonds and Notes)",
    "CT": "Cryptocurrency",
    "DB": "Defined Benefit Pension",
    "DO": "Debts Owed to the Filer",
    "DS": "Delaware Statutory Trust",
    "EF": "Exchange Traded Funds (ETF)",
    "EQ": "Excepted/Qualified Blind Trust",
    "ET": "Exchange Traded Notes",
    "FA": "Farms",
    "FE": "Foreign Exchange Position (Currency)",
    "FN": "Fixed Annuity",
    "FU": "Futures",
    "GS": "Government Securities and Agency Debt",
    "HE": "Hedge Funds & Private Equity Funds (EIF)",
    "HN": "Hedge Funds & Private Equity Funds (non-EIF)",
    "IC": "Investment Club",
    "IH": "IRA (Held in Cash)",
    "IP": "Intellectual Property & Royalties",
    "IR": "IRA",
    "MA": "Managed Accounts (e.g., SMA and UMA)",
    "MF": "Mutual Funds",
    "MO": "Mineral/Oil/Solar Energy Rights",
    "OI": "Ownership Interest (Holding Investments)",
    "OL": "Ownership Interest (Engaged in a Trade or Business)",
    "OP": "Options",
    "OT": "Other",
    "PE": "Pensions",
    "PM": "Precious Metals",
    "PS": "Stock (Not Publicly Traded)",
    "RE": "Real Estate Invest. Trust (REIT)",
    "RF": "REIT (EIF)",
    "RP": "Real Property",
    "RS": "Restricted Stock Units (RSUs)",
    "SA": "Stock Appreciation Right",
    "ST": "Stocks (including ADRs)",
    "TR": "Trust",
    "VA": "Variable Annuity",
    "VI": "Variable Insurance",
    "WU": "Whole/Universal Insurance"
}


class TransactionFactory:
    @staticmethod
    def from_transaction_string(transaction_str: str, ptr_id: int):
        """
        Given a transaction string and ptr filing id, create the pertinent transaction object

        Args:
            transaction_str: str, string value of transaction information taken from a PTR Filing pdf file
            ptr_id: int, ptr filing id that the transaction string came from
        """
        try:
            # Begin by getting the asset type to determine what kind of object should be created
            asset_type = get_asset_type(transaction_str)
            if asset_type in SUPPORTED_ASSETS:
                # Parse the string into a tuple of all the necessary information
                params = parse_string(asset_type=asset_type, transaction_str=transaction_str, ptr_id=ptr_id)
                if asset_type in SPECIALIZED:
                    # If the asset type is specialized, parse the asset name for the possible ticker
                    ticker, asset_name = get_stock_name(params[3])
                    match asset_type:
                        case 'ST':
                            return Stocks(params, ticker=ticker, asset_name=asset_name)
                        case 'CT':
                            # This one is reversed, typically the name is in parentheses, not the ticker
                            return Cryptocurrency(params, nickname=asset_name, asset_name=ticker)
                        case 'OP':
                            return Options(params, description=get_op_description(), asset_name=asset_name, ticker=ticker)
                else:
                    return Transaction(*params)
            else:
                print(f'Unfortunately there is no implementation for a {ASSET_CODES[asset_type]} transaction yet.')
                return None
        except Exception as e:
            with open('error_log.txt', 'a') as error_file:
                error_file.write(f'Could not create a transaction from {ptr_id}: {transaction_str} - {e}\n')
            return None

    @staticmethod
    def from_db_tuple(db_tuple):
        """
        Given a tuple returned from the database, convert the information into a transaction object

        Args:
            db_tuple: a record from the database returned as a tuple
        """
        # Unpack the tuple from the database into properly named variables
        tran_id, ptr_id, asset_type, owner, asset_name, ticker, description, nickname, type, minimum, maximum, ex_date, notified = db_tuple

        # Repackage the necessary items into a tuple that can be passed into any transaction object init
        transaction_params = (asset_type, ptr_id, owner, asset_name, type, minimum, maximum, ex_date, notified)
        try:
            if asset_type in SUPPORTED_ASSETS:
                if asset_type in SPECIALIZED:
                    # If the asset type is specialized, pass in all kwargs that could pertain to each
                    return SPECIALIZED[asset_type](transaction_params, ticker=ticker, description=description, nickname=nickname, asset_name=asset_name)
                else:
                    return Transaction(*transaction_params)
            else:
                print(f'Unfortunately there is no implementation for a {ASSET_CODES[asset_type]} transaction yet.')
                return None
        except Exception as e:
            with open('error_log.txt', 'a') as error_file:
                error_file.write(f'Could not create a transaction from database tuple: {e}\n')
            return None

    @staticmethod
    def to_db_tuple(t: Transaction):
        """
        Given a transaction object, prepare it to be inserted into the database by converting its attributes into the
        correct information in the format of a tuple

        Args:
            t: Transaction object that will be inserted into the database

        Returns:
            tuple of the transaction object information
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


__all__ = ['TransactionFactory', 'Transaction']
