from src.data import Data, Course, Lecture

def download_course() -> bool:
    
    data = Data()
    data.get_course_link()


    credentails = data.get_credentials()
    data.main_request(credentails)


    data.create_file_structure_and_download()


if __name__ == "__main__":
    download_course()