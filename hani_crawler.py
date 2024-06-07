import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

hani_url = "https://www.hani.co.kr"
headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"}

def write_csv_file(url, title, content):

    # 결과를 저장할 폴더 생성
    result_dir = 'result'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # CSV 파일 경로 설정
    csv_file_path = os.path.join(result_dir, 'hani_news2.csv')

    # csv 파일에 데이터 쓰기
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'title', 'content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 파일이 존재하지 않으면 헤더를 쓰기
        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({'url': url, 'title': title, 'content': content})

def fetch_articles(href):
    try:
        url = hani_url + href
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')

            json_data = soup.select_one('#__NEXT_DATA__').get_text()

            # JSON 데이터 파싱
            parsed_data = json.loads(json_data)

            # created_date_str = parsed_data['props']['pageProps']['article']['createDate']
            # created_date = datetime.strptime(created_date_str, '%Y-%m-%d %H:%M')
            # now = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
            # yesterday = now - timedelta(days=1)

            # if(created_date <= now and created_date > yesterday):

            # "title" 값을 추출
            title = parsed_data['props']['pageProps']['article']['title']
            print("Title: ", title)
            # print("Date: ", created_date)

            content = parsed_data['props']['pageProps']['article']['content']
            content = re.sub(r'<[^>]+>', '', content)
            content_without_images = re.sub(r'\[%%IMAGE\d+%%\]', '', content)

            write_csv_file(url, title, content_without_images)
            
            # else:
            #   return

    except Exception as e:
        print(f"Error fetching article {href}: {e}")

def fetch_list_url(page):
    list_url = hani_url + "/arti?page=" + str(page)

    res = requests.get(list_url, headers=headers, timeout=10)

    if res.status_code == 200:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')

        links = soup.select('#__next > div > div > div.section_inner__Gn71W > div.section_flexInner__jGNGY.section_content__CNIbB > div.section_left__5BOCT > div > ul > li > article > a')

        # 각 링크의 href 속성 가져오기
        hrefs = [link.get('href') for link in links]
        return hrefs
    return []

def hani_crawler():
    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_page = {executor.submit(fetch_list_url, i): i for i in range(1, 200)}

        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                hrefs = future.result()
                if hrefs:
                    with ThreadPoolExecutor(max_workers=10) as article_executor:
                        article_futures = [article_executor.submit(fetch_articles, href) for href in hrefs]
                        for article_future in as_completed(article_futures):
                            article_future.result()
            except Exception as e:
                print(f"Error processing page {page}: {e}")

if __name__ == "__main__":
    hani_crawler()
