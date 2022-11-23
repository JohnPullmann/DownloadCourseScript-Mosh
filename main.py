# from bs4 import BeautifulSoup
# import requests

# def convert_to_html(url) :
#     result = requests.get(url).text
#     return BeautifulSoup(result, "html.parser")

# def download_video(name, url):
#     response = requests.get(url)
        
#     with open(name, "wb") as video:
#             video.write(response.content)
            
    
# doc = convert_to_html("https://codewithmosh.com/courses/python-programming-course-beginners/lectures/6781576")

# group_videos = doc.find_all(class_="col-sm-12 course-section")

# for chapter in group_videos:
    
#     idx = 0 
#     for video in chapter.find_all(class_="section-item incomplete")[:4]:
#         video = "https://codewithmosh.com/" + video.get("data-lecture-url")
        
#         doc = convert_to_html(video)
#         download_video_btn = doc.find_all(name="a", class_="download")[0].get("href")
        
#         idx += 1
#         download_video(f"video{idx}.mp4", download_video_btn)

from src.data import Data

def download_course() -> bool:
    data = Data()
    
    
    data.get_credentials()


if __name__ == "__main__":
    download_course()