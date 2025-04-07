from ptr_filing import PTRFiling
import xml.etree.ElementTree as ET
from datetime import datetime
import os


def parse_xml(year: int) -> [PTRFiling]:
    """
    Given a year as a string, the corresponding XML file will be parsed for the Periodic Transaction Report IDs

    3/19 Changing this function to a generator function that will yield a tuple of the representative's name and PTR id,
    this could ultimately help to prevent a bunch of pdfs from being downloaded all at once? but it will also keep the
    webdriver open longer and spread out the downloading over a longer period of time, may be worth it to just keep as
    is and download all at the same time

    Args:
        year: int, int value of a year that matches the name of a corresponding XML financial disclosures file

    Return:
        [PTRFiling]: list of PTRFiling objects containing attributes for rep name, filing id and date
    """
    try:
        file_name = f'{year}FD.xml'
        # Open the XML file and get the root of it
        tree = ET.parse(file_name)
        root = tree.getroot()

        # Create a holder for all the PTR Filing objects
        ptr_filings = []

        # Check every child of the root in the XML to see if the filing type is a Periodic Transaction Report (P)
        for child in root:
            if child.find('FilingType').text == 'P':
                # There are two types of PRT filings, one begins with a 2 and is a typed version of the disclosures, the
                # begins with an 8 and is handwritten and there is no easy way to gather information from it
                ptr_id = child.find('DocID').text
                if ptr_id[0] == '2':
                    name = child.find('First').text + ' ' + child.find('Last').text
                    filing_date = datetime.strptime(child.find('FilingDate').text, "%m/%d/%Y")

                    # Create the filing object with the extracted information and append to the list of objs
                    filing = PTRFiling(rep_name=name, ptr_id=int(ptr_id), filing_date=filing_date)
                    ptr_filings.append(filing)

        # Clean up and remove the XML file once it's been parsed
        os.remove(file_name)

        return ptr_filings
    except Exception as e:
        print(f'Something went wrong while trying to parse the {year}FD.xml file: {e}')
        return []
