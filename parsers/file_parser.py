import os
from pypdf import PdfReader


def parse_pdf(ptr_id: int) -> []:
    """
    Given a PTR ID, open the pdf file corresponding to the ID, extract all the relevant lines and pass to convert the
    list of strings into a list of Transaction objects

    Args:
        ptr_id: int, integer value of a PTR ID, this will be used to open the corresponding pdf file report

    Return:
        [Transaction], list of transaction objects that are created from the contents of a PTR report
    """
    # Every PTR report has the following string at the end of the table of transactions, this will be searched for to
    # indicate the end of the table in each file
    end_file_cue = "* For the complete list of asset type abbreviations, " \
                   "please visit https://fd.house.gov/reference/asset-type-codes.aspx."

    try:
        # Use the PDF Reader to open the PDF file
        reader = PdfReader(f'{str(ptr_id)}.pdf')

        # Holder for the list of string contents from the PDF
        contents = []
        # This is going to be switched to False once the end cue has been found to stop parsing through the file
        end_not_reached = True

        for page in range(len(reader.pages)):
            if end_not_reached:
                # Split a page by the new line character
                page_contents = reader.pages[page].extract_text().split('\n')

                if '$200?' in page_contents:
                    page_contents = page_contents[page_contents.index('$200?')+1:]
                else:
                    end_not_reached = False

                if end_file_cue in page_contents:
                    page_contents = page_contents[:page_contents.index(end_file_cue)]
                    end_not_reached = False
                elif page == 0:
                    page_contents = page_contents[:-1]

                contents += page_contents
            else:
                break
        # Pass the PDF contents to the conversion function to turn them into Transaction objects
        transaction_tuples = _pdf_to_transactions(contents, ptr_id)

        # Clean up and delete each PDF file once the contents have been extracted
        os.remove(f"{os.getcwd()}\\{str(ptr_id)}.pdf")

        return transaction_tuples
    except Exception as e:
        print(f'Something went wrong while extracting contents from PTR {ptr_id}: {e}')


def _pdf_to_transactions(contents: [str], ptr_id: int) -> []:
    """
    Given the contents of a PDF file broken up line by line, parse through the lines and build Transaction objects, and
    return a list of transaction objects for the file

    Args:
        contents: [str], list of strings which are the contents of a PDF file
        ptr_id: the Periodic Transaction Report id associated with the PDF file

    Return:
        [Transaction], list of Transaction objects for a single PDF report
    """
    pdf_transactions = []
    try:
        # 'F\x00: Filing Status:
        # 'S\x00: Subholding of:
        # 'L\x00: # TODO: Find out what L starts
        # 'D\x00: Description
        # 'C\x00: Comments
        transaction_str = ""
        for x in range(len(contents)):
            content_line = contents[x]
            transaction_str += content_line + " "

            note_codes = ['F\x00', 'S\x00', 'L\x00', 'D\x00', 'C\x00']

            # In an attempt to make the next if block more readable, the conditions are broken down here

            # If the content line contains the 'Comment' note code, it is the last line for the transaction
            has_comment = content_line.find('C\x00') != -1
            # Check if it is the last line of the provided list
            is_last_line = x == len(contents)-1

            # The next three conditions must all be met to indicate it is the end of a transaction

            # If the current line has one of the note codes listed above
            has_note_code = content_line[:2] in note_codes
            # And this is not the last line in the provided list
            is_not_last = x+1 < len(contents)
            if is_not_last:
                # And the next line does not contain one of the note codes, this indicates it is the last line
                next_has_note_code = contents[x+1][:2] not in note_codes
            else:
                next_has_note_code = False
            last_note_code = has_note_code and is_not_last and next_has_note_code

            # If there's comment note, is last line, or has a note code but the next line doesn't, and is for a Stock
            if has_comment or is_last_line or last_note_code:
                pdf_transactions.append((transaction_str, ptr_id))
                transaction_str = ""
        return pdf_transactions
    except Exception as e:
        print(f'Something went wrong while parsing the {ptr_id} PDF contents: {e}')
