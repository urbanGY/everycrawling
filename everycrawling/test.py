import requests
from lxml import html
from bs4 import BeautifulSoup
#왓챠는 가능
url = 'https://movie.naver.com/movie/search/result.nhn?query=%EB%B2%94%EC%A3%84%EC%99%80%EC%9D%98+%EC%A0%84%EC%9F%81&section=all&ie=utf8'

url = 'http://search.maxmovie.com/search/?sword=%EB%B2%94%EC%A3%84%EC%99%80%EC%9D%98%20%EC%A0%84%EC%9F%81%3A%20%EB%82%98%EC%81%9C%EB%86%88%EB%93%A4%20%EC%A0%84%EC%84%B1%EC%8B%9C%EB%8C%80'

url = 'https://search.daum.net/search?q=%EB%B2%94%EC%A3%84%EC%99%80%EC%9D%98+%EC%A0%84%EC%9F%81%3A+%EB%82%98%EC%81%9C%EB%86%88%EB%93%A4+%EC%A0%84%EC%84%B1%EC%8B%9C%EB%8C%80&w=tot&DA=S43'
url = 'https://watcha.com/ko-KR/search?query=%EB%B2%94%EC%A3%84%EC%99%80%EC%9D%98%20%EC%A0%84%EC%9F%81'
page = requests.get(url)
tree = html.fromstring(page.content)
result = tree.xpath('//*[@id="root"]/div/div[1]/section/section/section[2]/div[2]/div[1]/div/div/div/ul/li[@*]/a/div[2]/div[1]')
print(result[0].text_content())
# soup = BeautifulSoup(page, 'html.parser')
# result = soup.find('div',class_='css-14v2c4p-ResultTitle eldorhe1').get_text()
# print(result)
