import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import os

hani_url = "https://www.hani.co.kr"
headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"}

def write_csv_file(url, title, content):

  # 결과를 저장할 폴더 생성
  result_dir = 'result'
  if not os.path.exists(result_dir):
      os.makedirs(result_dir)

  # CSV 파일 경로 설정
  csv_file_path = os.path.join(result_dir, 'hani_news.csv')

  # csv 파일에 데이터 쓰기
  with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
      fieldnames = ['url', 'title', 'content']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

      # 파일이 존재하지 않으면 헤더를 쓰기
      if csvfile.tell() == 0:
          writer.writeheader()

      writer.writerow({'url': url, 'title': title, 'content': content})

def fetch_articles(href):

  url = hani_url + href
  res = requests.get(url, headers=headers)

  if res.status_code == 200:
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    json_data = soup.select_one('#__NEXT_DATA__').get_text()

    # JSON 데이터 파싱
    parsed_data = json.loads(json_data)

    # "title" 값을 추출
    title = parsed_data['props']['pageProps']['article']['title']
    print("Title: ", title)

    content = parsed_data['props']['pageProps']['article']['content']
    content = re.sub(r'<[^>]+>', '', content)
    content_without_images = re.sub(r'\[%%IMAGE\d+%%\]', '', content)

    print("Content: ", content_without_images)

    write_csv_file(url, title, content_without_images)


def fetch_list_url():

  for i in range(1, 1000000):

    list_url = hani_url + "/arti?page=" + str(i)

    res = requests.get(list_url, headers=headers)

    if res.status_code == 200:
      html = res.text
      soup = BeautifulSoup(html, 'html.parser')

      links = soup.select('#__next > div > div > div.section_inner__Gn71W > div.section_flexInner__jGNGY.section_content__CNIbB > div.section_left__5BOCT > div > ul > li > article > a')

      # 각 링크의 href 속성과 텍스트 가져오기
      for link in links:
          href = link.get('href')  # href 속성 가져오기
          fetch_articles(href)


def hani_crawler():

  fetch_list_url()

if __name__ == "__main__":

  crawled_data = hani_crawler()