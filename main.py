import undetected_chromedriver as uc
from src.data import Data, Course, Lecture
from src.logging_setup import logger
import os

os.system("color")

def download_course() -> bool:
    driver = uc.Chrome()
    
    data = Data()
    data.get_course_links()
    
    credentails = data.get_credentials()
    data.log_in_to_website(credentails=credentails, driver=driver)

    for link in data.links_array:
        data.get_html_information(driver=driver, link=link)
        data.create_file_structure_and_download(driver=driver)


if __name__ == "__main__":
    download_course()