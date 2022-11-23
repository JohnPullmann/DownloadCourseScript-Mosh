

class Data():
    links_array = []
    
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
        pass

    def main_request(self) -> bool:
        pass

    def create_structure(self) -> bool:
        pass

    def download_lecture(self) -> bool:
        pass