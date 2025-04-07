# Government Stock Portfolio Project #
A project that gathers and parses all the financial disclosures by government officials and stores the information into
a database.

## Data Aggregator Overview ##
A data aggregator is used to gather all the data that is stored in this database. It is currently done through a
Selenium webdriver that will download the latest zip folder from the Financial Disclosures website which contains an XML
file with all the filings that have been made in the current year. 

The XML file is then iterated through to find all Periodic Transaction Reports (PTR), all new filings will be
downloaded and then parsed for their transaction information. Once transactions have been created, they are then
inserted into the database.

## Data Aggregator In-Depth Look ##
1. A Selenium webdriver is created with specific preferences, these are to set the download location from the default Downloads folder to the current working directory and that any url visited that is a PDF file should be downloaded
    ```python
    prefs = {
                "download.default_directory": path_to_here,  # Set download folder
                "download.prompt_for_download": False,  # Disable download prompt
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,  # Ensure safe downloads
                "plugins.always_open_pdf_externally": True  # Should force PDFs to download?
            }
    ```
2. The webdriver visits the Financial Disclosures website and selects the Zip folder link for the current year
3. The zip folder contents are extracted, the additional .txt file and folder are immediately deleted, leaving the XML
4. Iterate the children of the XML root in search of filings that match the following conditions:
   1. `FilingType == P`
   2. The first digit of the `DocID == 2`
5. The returned list are all the reported PTRs, get all current PTRs in the database and download only the ones that are not in the database yet
6. By this point all the new filing PDFs will have been downloaded, for each new filing, perform the following:
   1. Trim the top of the PDF down to where the transaction table begins
      1. If necessary, trim the end of the PDF as well, this removes PTR id or disclosure information
   2. Split the remainder of the PDF line by line
   3. The lines of the PDF will then be concatenated into single strings that make up a row of the transaction table
7. Each transaction string is then parsed and the necessary information to create a Transaction object are extracted
   
   | Attribute  |    Type     | Notes                                          |
   |------------|:-----------:|------------------------------------------------|
   | asset_type |     str     | Type of asset the transaction is pertaining to |
   | ptr_id     |     int     | The PDF filing id                              |
   | owner      | str or None |                                                |
   | asset_name |     str     |                                                |
   | type       |     str     | Purchase (P), Sell (S) or E(?)                 |
   | minimum    |     int     |                                                |
   | maximum    |     int     |                                                |
   | executed |  datetime   | Date the trade was executed                    |
   | notified |  datetime   | Date the trade was filed to be reported        |

8. There are subclasses to the parent Transaction object such as Stocks, Options, and Cryptocurrency, the additional information each one has is as follows:
   1. Stocks: Stock ticker for the asset
   2. Options: Stock ticker for the asset, and Description of the option exercised or purchased
   3. Cryptocurrency: Nickname/ticker of the cryptocurrency
9. All the extracted information is inserted into the database: (See below for Database Schema)
   1. Beginning with any new representatives that have newly filed
   2. New PTR Filings
   3. All new transactions

# Database #
In order to set up the database structure properly before running the data aggregator, the `startup.py` **must be run first**.
This can be done manually or by running the `install.bat` file.

## Database Schema ##
There are three tables in the database *representatives*, *ptr_filings*, and *transactions*.

### Representatives Table ###
| Field | Type | Notes |
| ----- | :--: | :---- |
| id | int | Primary Key -> ptr_filings.rep_id |
| name | str |

### PTR Filings Table ###
| Field | Type | Notes |
| ----- | :--: |:------|
| ptr_id | int | Primary Key -> transactions.ptr_id |
| rep_id | int | Foreign Key -> representatives.id |
| date | datetime | |

### Transactions Table ###
| Field |   Type   | Notes                             |
| ----- |:--------:|:----------------------------------|
| transaction_id |   int    | Primary Key                       |
| ptr_id |   int    | Foreign key -> ptr_filings.ptr_id |
| asset_type         |   str    | Not NULL                          |
| owner             |   str    |                                   |
| asset_name       |   str    | Not NULL                          |
| ticker          |   str    |                                   |
| description    |   str    |                                   |
| nickname      |   str    |                                   |
| type         |   str    | Not NULL                          |
| minimum     |   int    | Not NULL                          |
| maximum    |   int    | Not NULL                          |
| executed  | datetime | Not NULL                          |
| notified | datetime | Not NULL                          |