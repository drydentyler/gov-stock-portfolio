from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import zipfile
from selenium.webdriver.common.by import By


class Webdriver:
    def __init__(self, sim_mode=False):
        # Get the current year, this will be used to search for correct zip files/xml
        self.year = datetime.now().year

        # Get the current working directory, zip files will be saved and read here
        self.path_to_here = os.getcwd()

        self.driver = self._create_driver() if not sim_mode else None

    def _create_driver(self) -> webdriver:
        # Set up the chrome options to save any downloaded files to this directory
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.path_to_here,  # Set download folder
            "download.prompt_for_download": False,  # Disable download prompt
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,  # Ensure safe downloads
            "plugins.always_open_pdf_externally": True  # Should force PDFs to download?
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Navigate to the financial disclosures site and download the latest zip file
        return webdriver.Chrome(options=chrome_options)

    def download_latest_zip(self) -> int:
        """
        Goes to the Financial Disclosures website and tries to download the most recent XML file of disclosure reports

        Returns:
            int: 1 if successful, 0 if something went wrong
        """
        try:
            # This is the website where the latest Periodic Transaction Reports are posted in a zip file
            starting_url = "https://disclosures-clerk.house.gov/FinancialDisclosure"

            self.driver.get(starting_url)

            # Find the latest year by searching for it by link text
            latest_zip = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, str(self.year))))
            latest_zip.click()

            # Set a variable to the path to the downloaded zip file
            zip_path = self.path_to_here + '\\' + f"{self.year}FD.zip"

            # Create a wait here for the zip file to be completely downloaded
            while not os.path.exists(zip_path):
                print('Waiting to download zip file . . .')
                time.sleep(1)

            # Extract the contents of the zip file to the current directory
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.path_to_here)

            # There will also be a txt file and the zip folder remaining, delete these since they aren't used
            for file_type in ['.txt', '.zip']:
                file_name = f'{self.year}FD{file_type}'
                if os.path.exists(file_name):
                    os.remove(file_name)

            return 1
        except Exception as e:
            print(f'Something went wrong while downloading the Financial Disclosures XML file: {e}')
            return 0  # 1

    @staticmethod
    def _get_ptr_url(url_year: str, doc_id: str):
        return f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{url_year}/{doc_id}.pdf"

    def download_prt_pdfs(self, ptr_ids: [int]) -> int:
        """
        Given a list of PTR report IDs, download each PDF file

        Args:
            ptr_ids: [int], list of integers representing the PTR file IDs

        Return:
            int, 1 if successfully downloaded all the files, 0 if something went wrong
        """
        try:
            for ptr in range(len(ptr_ids)):
                print(
                    f'Downloading PTR PDF files: {round(((ptr + 1) / len(ptr_ids)) * 100, 2)}% complete . . . {ptr_ids[ptr]}')
                self.driver.get(self._get_ptr_url(str(self.year), ptr_ids[ptr]))
            return self._wait_pdf_downloads()
        except Exception as e:
            print(f'Something went wrong while downloading PTR PDF files: {e}')
            return 0

    @staticmethod
    def _wait_pdf_downloads() -> int:
        """
        Gives 60 seconds for all PDF downloads to finish, checking in on them every 2 seconds

        If a file is not done downloading, it will have the extension .crdownload

        Return:
            int, 1 if all PDFs are downloaded, 0 if not all finished
        """
        print('Starting to wait for PTR PDFs to finish downloading.')
        start_time = time.time()
        while time.time() - start_time < 60:
            if not any(filename.endswith('.crdownload') for filename in os.listdir(os.getcwd())):
                print('Downloads are all complete.')
                return 1
            print('. . .')
            time.sleep(2)

        print('Warning: Some PDFs did not complete downloading.')
        return 0
