from selenium import webdriver              # 웹사이트(및 웹 애플리케이션)의 유효성 검사에 사용되는 자동화 테스트 프레임워크
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime

url = 'https://kr.iherb.com/'
options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
options.add_argument('user-agent=' + user_agent)
options.add_argument('lang=ko_KR')

# 크롬 드라이버 최신 버전 설정
service = ChromeService(executble_path=ChromeDriverManager().install())
# 크롬 드라이버
driver = webdriver.Chrome(service=service, options=options)

category = ['seasonal-allergies', 'sleep', 'weight-loss', 'childrens-health', 'mens-health', 'womens-health']
category_kr = ['계절성 알레르기', '불면증', '체중 조절', '어린이 건강', '남성 건강', '여성 건강']
# pages = [14, 13, 14, 16, 8, 16]  # 각 카테고리 별 총 페이지 수
pages = [13, 13, 13, 13, 8, 13]    # 학습을 위해 최대 페이지를 중간 값인 13 페이지로 제한함
df_titles = pd.DataFrame()



for i in range(6):
    # 카테고리 변경
    section_url = 'https://kr.iherb.com/c/{}'.format(category[i])
    df_titles = pd.DataFrame()
    titles = []                 # titles 초기화
    product = 49                # 제품 수 초기화
    for j in range(1, 3):       # pages[i]+1 (시간 문제 상 3으로 축소)
        if j == 1:
            url = section_url
        else:
            url = section_url + '?p={}'.format(j)        # 페이지 변경
        driver.get(url)
        time.sleep(2)
        for k in range(1, product):
            try:
                print('%d' %k)
                xpath_temp = '/html/body/div[7]/div/div[3]/div/div/div[1]/div[1]/div[2]/div[2]/div[{}]/div/div[2]/div[1]/a'.format(k)
                driver.find_element('xpath', xpath_temp).click()        # 클릭시 사이트로 이동
                time.sleep(3)                                               # 클릭 후 사이트로 이동할 대기 시간 부여
                print('debug%d, %d'%k %product)

                # 제품 설명 크롤링
                nutrient_data1 = driver.find_element('xpath',
                                                    '/html/body/div[8]/article/div[2]/div/section/div[2]/div/div/div[1]/div[1]/div/div/ul').text
                # 제품 설명 전처리 (한글, 영어(대,소문자), 숫자만 수집. 그 외는 공백 처리)
                nutrient_data1 = re.compile('[^가-힣|a-z|A-Z|0-9]').sub(' ', nutrient_data1)
                titles.append(nutrient_data1)

                # nutrient_data2 = driver.find_element('xpath',
                #                                     '/html/body/div[8]/article/div[2]/div/section/div[2]/div/div/div[1]/div[1]/div/div/p[2]').text
                # nutrient_data2 = re.compile('[^가-힣|a-z|A-Z|0-9]').sub(' ', nutrient_data2)
                # titles.append(nutrient_data2)

                driver.back()           # 사이트 뒤로 가기
                time.sleep(5)           # 이전 사이트로 이동할 대기 시간 부여

            except:
                product = product + 1   # 제품 번호를 건너뛸 경우 empty 수를 1 씩 늘림
                # 오류가 발생할 경우 error + 카테고리, 페이지, 제품 번호 출력
                print('error {} {} {}'.format(i, j, k))

    df_section_title = pd.DataFrame(titles, columns=['titles'])
    df_section_title['category'] = category_kr[i]
    df_titles = pd.concat([df_titles, df_section_title], ignore_index=True)

    # crawling 폴더에 Nutrients_(카테고리)_(년월일).cvs 파일로 저장
    df_titles.to_csv(
        './crawling_data/Nutrients_{}_{}.csv'.format(category[i], datetime.datetime.now().strftime('%Y%m%d')),
        index=False)

print(df_titles.head(20))  # 상위 제목 20개 출력
df_titles.info()
print(df_titles['category'].value_counts())
