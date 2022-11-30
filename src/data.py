import re

class Data():
    links_array = []
    courses_data = []
    
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




        with open("credentials.txt", 'r') as file:
            lines = file.read().splitlines()

        if len(lines) < 2:
            print("Invalid content format of creadentials.txt")
            email = input_email()
            password = input_password()
            write_to_credentials(email=email, password=password)
        else:
            email = lines[0]
            password = lines[1]

        if len(email) < 6 or len(password) < 6:
            print("Invalid content format of creadentials.txt")
            email = input_email()
            password = input_password()
            write_to_credentials(email=email, password=password)

        elif email[0:6] != "email:" or password[0:9] != "password:":
            print("Invalid content format of creadentials.txt")
            email = input_email()
            password = input_password()
            write_to_credentials(email=email, password=password)

        # test if email is valid
        email = email.split(" ")[1]
        if email == "" or validate_email(email) == False:
            email = input_email()
            write_to_credentials(email=email)
        
        # test or get password
        password = password.split(" ")[1]
        if password == "":
            password = input_password()
            write_to_credentials(password=password)

        return {"email": email, "password": password}

    def main_request(self) -> bool:
        pass

    def create_structure(self) -> bool:
        pass


class Course(Data):
    def __init__(self, name, time):
        self.name = name
        self.time = time
        self.sections = {}

        Data.courses_data.append(self)

        
    def add_section(self, lecture_name: str):
        self.sections[lecture_name] = []

    def add_lecture(self, section_name: str, lecture_link: str, lecture_name: str, lecture_id: str):
        lecture = Lecture(lecture_name, lecture_id, lecture_link)
        self.lectures[section_name].append(lecture)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.time})"


class Lecture(Course):
    def __init__(self, name: str, id: str, link: str):
        self.name = name 
        self.id = id 
        self.url = "https://codewithmosh.com/" + link

        
    def download_lecture(self) -> bool:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.id})"
