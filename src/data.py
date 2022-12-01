import re
from bs4 import BeautifulSoup
import requests
import urllib
import os
import ntpath

class Data():
    links_array = []
    courses_data = []
    
    def __init__(self):
        self.is_internet_connect()
    
    def is_internet_connect(self, host="http://google.com"):
        try:
            urllib.request.urlopen(host)
        except:
            raise Exception("You don't have internet connection!")
        

    def get_course_link(self) -> bool:
        with open("course_links.txt", 'r') as file:
            
            empty_line = 0
            file_content = file.read().splitlines()
            for url in file_content:
                
                if url.find("http") != -1:
                    self.links_array.append(url)
                elif url == '':
                    empty_line += 1
                else:
                    raise Exception("Something is wrong with the url address!")
                    
                if empty_line == len(file_content):
                    raise Exception("File 'course_links.txt' is empty!")
                
        return True

    def get_credentials(self) -> dict:

        def validate_email(email: str) -> bool:
            email_pattern =  r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if (re.fullmatch(email_pattern, email)):
                return True
            return False
        
        def input_email() -> str:
            email = ""
            while email == "" or validate_email(email) == False:
                print("Email is invalid!")
                email = input("Change credentials.txt or Enter email: ")
            return email
                
        def input_password() -> str:
            password = ""
            while password == "" or ' ' in password:
                print("Password is invalid!")
                password = input("Change credentials.txt or Enter password: ")
            return password

        def write_to_credentials(email: str = "", password: str = ""):
            with open("credentials.txt", 'r') as file:
                lines = file.read().splitlines()

            with open("credentials.txt", 'w') as file:
                
                if email != "":
                    file.write(f"email: {email}\n")
                else:
                    file.write(lines[0]+"\n")

                if password != "":
                    file.write(f"password: {password}")
                else:
                    file.write(lines[1]+"\n")

        def change_credentials() -> tuple[str, str]:
            print("Invalid content format of creadentials.txt")
            email = input_email()
            password = input_password()
            write_to_credentials(email=email, password=password)
            return (email, password)


        with open("credentials.txt", 'r') as file:
            lines = file.read().splitlines()

        if len(lines) < 2:
            email, password = change_credentials()
        else:
            email = lines[0]
            password = lines[1]

            if len(email) < 6 or len(password) < 6:
                email, password = change_credentials()

            elif email[0:6] != "email:" or password[0:9] != "password:":
                email, password = change_credentials()

            else:
                email = email.split(" ")[1]
                password = password.split(" ")[1]

        # test if email is valid
        if email == "" or validate_email(email) == False:
            email = input_email()
            write_to_credentials(email=email)
        
        # test or get password
        if password == "":
            password = input_password()
            write_to_credentials(password=password)

        return {"email": email, "password": password}


    def main_request(self, credentails) -> requests.sessions.Session:
        
        def log_in():
            
            session = requests.Session()
            
            payload = {
                "email": credentails["email"],
                "password": credentails["password"]
            }
            
            session.post("https://sso.teachable.com/secure/146684/identity/login/password", data=payload)
            
            def valid_url_address():
                for link in self.links_array:
                    
                    r = session.get(link)
                    response = r.status_code
                    
                    if 200 <= response <= 299:
                        pass
                    else:
                        raise Exception(f"[{response} Error]: {link}")
                    
                return True 
            
            if valid_url_address():
                pass
            
            return session
        
        session = log_in()
        return session
    

    def create_structure(self) -> bool:
        def create_folders_path(path: str) -> bool:
            path = path.replace(os.sep, ntpath.sep)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except OSError:
                    print ("Creation of the directory %s failed" % path)
        
        create_folders_path("Courses/")
        for course in self.courses_data:
            path = "Courses/"+course.name+" - "+course.time+"/"
            create_folders_path(path)
            for section, lectures in course.sections.items():
                path = "Courses/"+course.name+" - "+course.time+"/"+section+"/"
                create_folders_path(path)
               


class Course(Data):
    def __init__(self, name: str, time: str = ""):
        self.name = name
        self.__time = time
        self.sections = {}

        Data.courses_data.append(self)

        
    def add_section(self, lecture_name: str):
        self.sections[lecture_name] = []

    def add_lecture(self, section_name: str, lecture_link: str, lecture_name: str, lecture_id: str):
        lecture = Lecture(lecture_name, lecture_id, lecture_link)
        self.sections[section_name].append(lecture)
    
    def get_cource_time(self) -> str:
        return "300h"
    
    @property
    def time(self) -> str:
        if self.sections:
            time = self.get_cource_time()
            self.__time = time
            return time
        else:
            print("Time of course couldn't be calculated because no sections were found. Please first add some sections!")
            return ""


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.__time})"


class Lecture(Course):
    def __init__(self, name: str, ID: str, link: str):
        self.name = name 
        self.id = ID 
        self.url = "https://codewithmosh.com/" + link

        
    def download_lecture(self) -> bool:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.id})"
