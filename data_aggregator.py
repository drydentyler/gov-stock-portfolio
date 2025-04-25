from transactions import Transaction, TransactionFactory
from parsers import parse_pdf, parse_xml
from datetime import datetime
from webdriver import Webdriver
from db_controller import DBController

db = DBController()
all_transactions: [Transaction] = []

# Create my webdriver with custom preferences to save any downloaded files to the current working directory
my_driver = Webdriver(sim_mode=False)

# Use the driver to download the latest XML file for financial disclosures, if it was successful continue
if my_driver.download_latest_zip():

    # Parse the XML file for all the necessary PTR file IDs
    # now returns a list of PTRFiling objects (name, id, filing date)
    ptr_ids = parse_xml(datetime.now().year)

    # Get the current records from the reps and ptr filings tables to compare the newly gotten values
    current_filings = [filing.id for filing in db.ptr_model.get_all_filings()]
    current_reps = {rep[1]: rep[0] for rep in db.rep_model.get_representatives()}
    new_filings = []

    for filing in ptr_ids:
        if filing.representative not in current_reps:
            # Representative is not currently in reps table, insert them
            new_id = db.rep_model.insert_rep(rep=filing.representative)
            if new_id != -1:
                # Update the current_reps table with the new rep name as key and the returned id as the value
                current_reps[filing.representative] = new_id
        if filing.id not in current_filings:
            # new ptr id, insert into ptr filings table, ptr_id, rep_id is value with rep name as key^
            """
            I don't love that this is going to run constantly for every new PTR Filing, I would rather have it run once
            with all new filings, but the trade off is that if an error occurs while inserting a large batch of them, 
            I would rather have some successes and have most of it inserted into the database and then sort out the few
            exceptions manually rather than have those hinder all the other records from getting inserted
            """
            successfully_added = db.ptr_model.insert_ptr_filing(ptr_id=filing.id,
                                                                rep_id=current_reps[filing.representative],
                                                                filing_date=filing.date)
            # If this was a new filing, add it to the list that will be used later for inserting transactions
            if successfully_added:
                new_filings.append(filing.id)

    # TODO: An issue that could occur is if an error occurs right here all new filings will be lost and not downloaded

    # Take the list of PTR IDs and download all the PDF files, if all were successfully downloaded, continue
    if my_driver.download_prt_pdfs(new_filings):

        print('#'*50)
        # Open each PDF file and parse its contents and create Transaction objects and concat onto all_transactions
        # for ptr in ptr_ids:
        for ptr in new_filings:
            transactions = [TransactionFactory.from_transaction_string(*transaction) for transaction in parse_pdf(ptr)]
            if transactions:
                all_transactions += transactions

########################################################################################################################

if all_transactions:
    db.tran_model.insert_transaction_batch(all_transactions)
    print(f'Inserted {len(all_transactions)} new transactions into the database.')

    """
    I'm going to keep this here because there may be times in the future when I want to write some of the transactions
    to txt files for debugging purposes:
    
    print(f'Created {len(all_transactions)} transactions.')
    for i in range(len(all_transactions)):
        t = all_transactions[i]
        print(f'Writing transaction results: {round(((i + 1) / len(all_transactions)) * 100, 2)}% complete . . .')
        try:
            with open(f'{t.asset_type}.txt', 'a') as file:
                match t.asset_type:
                    case 'ST':
                        line = f'{t.ex_date}~{t.asset_type}~{t.type}~{t.asset_name}~{t.ticker}~{t.minimum}~{t.maximum}'
                    case 'CT':
                        line = f'{t.ex_date}~{t.asset_type}~{t.type}~{t.asset_name}~{t.nickname}~{t.minimum}~{t.maximum}'
                    case 'OP':
                        line = f'{t.ex_date}~{t.asset_type}~{t.type}~{t.asset_name}~{t.ticker}~{t.minimum}~{t.maximum}~{t.description}'
                    case _:
                        line = f'{t.ex_date}~{t.asset_type}~{t.type}~{t.asset_name}~~{t.minimum}~{t.maximum}'

                file.write(line+'\n')
        except Exception as e:
            try:
                with open('error_log.txt', 'a') as error:
                    file.write(f'{t.ptr_id}: {e}\n')
            except Exception as ex:
                pass
    """
