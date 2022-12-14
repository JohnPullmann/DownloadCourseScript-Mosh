import re
from bs4 import BeautifulSoup
import requests
import urllib
import os
import ntpath
from src.logging_setup import logger
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys


class Data():
    links_array = []
    courses_data = []
    
    def __init__(self):
        self.is_internet_connect()
    
    def is_internet_connect(self, host: str="http://google.com"):
        try:
            urllib.request.urlopen(host)
        except:
            logger.exception("You don't have internet connection!")
            raise
        logger.debug("I am out")


    def validate_url_address(self, link: str) -> bool:
        
        try:
            r = requests.get(link)
            
        except Exception as e:
            raise ConnectionError(f"Someting is wrong with the url or server!\nurl: {link}")
        
        response = r.status_code
        if 200 <= r.status_code <= 299:
            return True
        else:
            raise Exception(f"[{response} Error]: {link}")


    def get_course_links(self) -> bool:
        with open("course_links.txt", 'r') as file:
            Data.n_links = 0
            file_content = file.read().splitlines()
            for url in file_content:
                
                if "http" in url or "https" in url:
                    if self.validate_url_address(link=url):
                        logger.info(f"Url address is correct: {url}")
                        Data.n_links += 1
                        self.links_array.append(url)
                elif set(url) == set(' ') or url == '':
                    pass
                else:
                    raise Exception("Something is wrong with the url address!")
                
            if Data.n_links == 0:
                raise Exception("File 'course_links.txt' is empty!")
        logger.info("Loading of courses from coure_links.txt was successful.")
        
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
                logger.warning("Email is invalid!")
                email = input("Change credentials.txt or Enter email: ")
            return email
                
        def input_password() -> str:
            password = ""
            while password == "" or ' ' in password:
                logger.warning("Password is invalid!")
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
            logger.warning("Invalid content format of creadentials.txt")
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

        logger.info("Loading of credentials was successful.")   
        return {"email": email, "password": password}
    
    
    def log_in_to_website(self, credentails: dict, driver, log_in_link: str="https://sso.teachable.com/secure/146684/identity/login/password") -> None:
        logger.info("Logging in to a website.")   
        driver.get(log_in_link)

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "email")))
        driver.find_element(By.ID, "email").send_keys(credentails["email"])
        time.sleep(3)

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "password")))
        driver.find_element(By.ID, "password").send_keys(credentails["password"])

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "btn-primary")))
        driver.find_element(By.CLASS_NAME, "btn-primary").click()

        #time.sleep(5)
        
        logger.info("Logging in successfully.\n\n")  
        
        
    def convert_into_html(self, driver, link: str, stop_video: bool = False):
        #time.sleep(5)
        driver.get(link)
        
        #time.sleep(6)
        # if stop_video: 
        #     print("Video", driver.find_element(By.TAG_NAME, "video"))
            # driver.find_element(By.TAG_NAME, "video").click()
        
        html = driver.page_source
        
        return html
        
    
    def get_html_information(self, driver, link: str):

        def get_rid_of_special_characters(element: str, better_time: bool = False) -> str:
            
            if better_time and '(' in element:
                element_time = element[element.rfind('(')+1:-1]
                element_time = element_time.replace(':','m') + 's'
                element = element[:element.rfind('(')] + element_time
                
            return "".join([x for x in element if x not in "/><:\"#\\|?!*,%[].'';:"])
            
        
        if self.validate_url_address(link=link):
            pass
        logger.info(f"Url address is correct: {link}")
        
        result = self.convert_into_html(driver=driver, link=link)

        soup = BeautifulSoup(result, "html.parser")
        
        course_name = soup.find(name="h2").text
        
        if "C#" in course_name:
            course_name = course_name.replace("C#", "C-Sharp")
        
        course_name = get_rid_of_special_characters(element=course_name)
        
        # Create Course
        course = Course(course_name)
        
        sec_idx = 1
        sections_array = soup.find_all(class_="col-sm-12 course-section")
        for section in sections_array:
            
            section_name = section.find(class_="section-title", role="heading").text.strip()

            try:
                section_name.index("(")
            except ValueError:
                logger.debug("Section {section_name} doesn't have time in title.")
                
                logger.debug("Calculating section time ...")
                s_time = 0

                lectures_array = section.find_all(class_="section-item")
                lec_idx = 1
                for lecture in lectures_array:
                    try:
                        lecture_name = lecture.find(name="span", class_="lecture-name").text.strip().replace("\n", " ")
                        minutes, seconds = lecture_name[lecture_name.rfind("(")+1:-1].split(":")
                        lecture_time = int(minutes)*60 + int(seconds)
                        s_time += lecture_time
                    except:
                        #lectures without time in name, ignore lecture time
                        logger.debug("Lecture doesn't have time in title.")
                        pass
                
                s_time = s_time // 60
                minutes, hours = s_time % 60, s_time // 60
                s_time = f"({f'{hours}h' if hours != 0 else ''}{minutes}{'m' if minutes != 0 else ''})"
                section_name = f"{section_name} {s_time}"

                logger.debug("Section time: {s_time}")



            if section_name.rfind("(") < section_name.rfind(":"):
                section_time = section_name[section_name.rfind("("):-1].replace(":","h") + 'm)'
                section_name = section_name[:section_name.rfind("(")] + section_time
            
            section_time = section_name[section_name.rfind("("):].replace(" min","m")
            section_name = section_name[:section_name.rfind("(")] + section_time
            
            if not section_name.strip()[0].isnumeric():
                section_name = f"{sec_idx}-{section_name}"
            
            section_name = get_rid_of_special_characters(element=section_name)
            course.add_section(section_name)
            
            lectures_array = section.find_all(class_="section-item")
            
            lec_idx = 0
            for lecture in lectures_array:
                lecture_name = lecture.find(name="span", class_="lecture-name").text.strip().replace("\n", " ")
                
                # The lecture is video 
                if '(' in lecture_name and ')' in lecture_name:
                    is_lecture = True
                    lec_idx += 1
                else:
                    is_lecture = False
                
                if "C#" in lecture_name:
                    lecture_name = lecture_name.replace("C#", "C-Sharp")
                    
                lecture_name = get_rid_of_special_characters(element=lecture_name, better_time=True)
                
                if not lecture_name.strip()[0].isnumeric():
                    lecture_name = f"{lec_idx}-{lecture_name}"
                
                    
                
                lecture_url = lecture.find(name="a", class_="item").get("href")
                lecture_id = lecture.find(name="a", class_="item").get("data-ss-lecture-id")
                
                if is_lecture:
                    course.add_lecture(section_name=section_name, lecture_link=lecture_url, lecture_name=lecture_name, lecture_id=lecture_id)
                else:
                    course.add_attachment(section_name=section_name, lecture_link=lecture_url, lecture_name=lecture_name, lecture_id=lecture_id)

            sec_idx += 1
            
        logger.info("Have html information.\n")

    def create_file_structure_and_download(self, driver) -> bool:
        
        def has_dir_all_lectures(path: str, lecture_list: list) -> bool:
            if os.path.exists(path):
                if len(os.listdir(path)) == len(lecture_list):
                    return True
                return False
                
            
        def create_folders_path(path: str) -> bool:
            path = path.replace(os.sep, ntpath.sep)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                    return True
                except OSError:
                    logger.warning(f"Creation of the directory {path} failed")
                    return False
            # else:
            #     if path != "Courses/":
            #         logger.info(f"Course already downloaded. Skipped course - {path}")
            #     return False

        logger.info("Creating file structure...\n")
        create_folders_path("Courses/")
        

        i_course = len(self.courses_data)
        course = self.courses_data[-1]
        logger.info(f"Course: {course.name} - {course.time} [{i_course}/{Data.n_links}]")
        path = f"Courses/{course.name} - {course.time}/"

        create_folders_path(path)
        i_section = 0
        for section, all_lectures in course.sections.items():
            i_section += 1
            path = f"Courses/{course.name} - {course.time}/{section}"

            create_folders_path(path)
            
            # logger.info(f"Starting downloading section: {section}...")
            print(" ")
            logger.info(f"Looking at section: {section} [{i_section}/{len(course.sections)}]")
            
            for i_lecture, lecture in enumerate(all_lectures):
                
                if f"{lecture.name}.mp4" not in os.listdir(path):
                    lecture.download_lecture(driver=driver, link=lecture.url, path=path, i=f"[{i_lecture+1}/{len(all_lectures)}]")
                    # logger.info(f"Section downloading successful.\n")
                    # logger.info(f"Lecture downloaded: {lecture.name}")
                else:
                    logger.info(f"Lecture already downloaded: {lecture.name}")

                lecture.download_lecture_attachment(driver=driver, link=lecture.url, path=path, i=f"{i_lecture+1}")
            logger.info(f"Section: {section} has all videos.\n")

        if course.attachments:
            logger.info(f"Downloading attachments:\n")
        for section, all_attachments in course.attachments.items():
            path = f"Courses/{course.name} - {course.time}/{section}"
            for attachment in all_attachments:
                attachment.download_lecture_attachment(driver=driver, link=attachment.url, path=path)
            
            
        logger.info(f"Course downloaded successful.\n\n\n\n")
        
        # status = create_folders_path(path)
        # if status:
        #     for section, lectures in course.sections.items():
        #         # path = "Courses/"+course.name+" - "+course.time+"/"+section+"/"
        #         path = f"Courses/{course.name} - {course.time}/{idx}-{section}"
        #         create_folders_path(path)


class Course(Data):
    def __init__(self, name: str, time: str = ""):
        self.name = name
        self.__time = time
        self.sections = {}
        self.attachments = {}
        
        Data.courses_data.append(self)

        
    def add_section(self, section_name: str):

        self.sections[section_name] = []
        self.attachments[section_name] = []

    def add_lecture(self, section_name: str, lecture_link: str, lecture_name: str, lecture_id: str):
        lecture = Lecture(lecture_name, lecture_id, lecture_link)
        self.sections[section_name].append(lecture)
    
    def add_attachment(self, section_name: str, lecture_link: str, lecture_name: str, lecture_id: str):
        lecture = Lecture(lecture_name, lecture_id, lecture_link)
        self.attachments[section_name].append(lecture)
    
    def get_cource_time(self) -> str:

        course_time = 0
        for section in self.sections:
            s = section.rfind("(")
            s_time = section[s+1:-1]
            if 's' not in s_time:
                if 'h' in s_time or 'm' in s_time:
                    if 'h' in s_time:
                        x = s_time.strip().split("h")
                        course_time +=  60 * int(x[0])
                        if 'm' in x[1]:
                            course_time += int(x[1][:-1])
                    else:
                        course_time += int(s_time[:-1])
                # else:
                #     x = s_time
                #     m = x[:2].strip()
                #     s = x[2:].strip()
                #     course_time +=  60 * int(m)
                #     course_time += int(s)

        minutes, hours = course_time % 60, course_time // 60
        course_time = f"{hours}{'h' if hours != 0 else ''}{minutes}{'m' if minutes != 0 else ''}"
        return course_time
    
    @property
    def time(self) -> str:
        if self.sections:
            course_time = self.get_cource_time()
            self.__time = course_time
            return course_time
        else:
            logger.warning("Time of course couldn't be calculated because no sections were found. Please first add some sections!")
            return ""


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.__time})"


class Lecture(Course):
    def __init__(self, name: str, ID: str, link: str):
        self.name = name 
        self.id = ID 
        self.url = "https://codewithmosh.com/" + link

    def download_progress_bar(self, video, response):
            # response = requests.get(download_btn, stream=True)
            total_length = response.headers.get('content-length')
            
            if total_length is None: # no content length header
                video.write(response.content)
            else:
                start = time.perf_counter()
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    video.write(data)
                    done = int(50 * dl / total_length)
                    # sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                    sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {self.name} -> {round(dl//1_000_000)}/{total_length//1_000_000} {round((dl//(time.perf_counter() - start))/1_000_000, 2)}Mbps") 
                    sys.stdout.flush()
        

    def download_lecture(self, link: str, path:str, driver, i: str) -> None:
        
        result = self.convert_into_html(driver=driver, link=link, stop_video=True)
        doc = BeautifulSoup(result, "html.parser")
        
        try:
            download_btn = doc.find_all(name="a", class_="download")[0].get("href")
            logger.info(f"Start downloading lecture {i}: {link}")
            
            response = requests.get(download_btn, stream=True)
            
            video_path = os.path.normpath(f"{path}/{self.name}.mp4")
            with open(video_path, "wb") as video:
                # video.write(response.content)
                self.download_progress_bar(video=video, response=response)
                
            print(" ")

        except IndexError:
            logger.warning(f"Download button wasn't found.")


    def download_lecture_attachment(self, link: str, path:str, driver, i: str = "") -> None:
        
        result = self.convert_into_html(driver=driver, link=link, stop_video=True)
        doc = BeautifulSoup(result, "html.parser")

        lecture_attachments = doc.find_all(name="a", class_="download")
        
        for lecture_attachment in lecture_attachments:
            attachment_name = None
            for line in lecture_attachment.text.split('\n'):
                if ".pdf" in line or ".zip" in line:
                    attachment_name = line
                    break
            
            if attachment_name != None:
    
                lecture_attachment_link = lecture_attachment.get("href")

                attachment_name = f"{i if i != '' else self.name.split('-')[0]}- {attachment_name}"

                if attachment_name not in os.listdir(path):
                    logger.info(f"Start downloading lecture attachment '{attachment_name}': {lecture_attachment_link}")
                    
                    response = requests.get(lecture_attachment_link, stream=True)
                    
                    attachment_path = os.path.normpath(f"{path}/{attachment_name}")
                    with open(attachment_path, "wb") as attachment:
                        # attachment.write(response.content)
                        self.download_progress_bar(video=attachment, response=response)

                    print(" ")
                else:
                    logger.info(f"Lecture attachment already downloaded: {attachment_name}")
            

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.id})"
