import pytest
import crawler

@pytest.fixture(scope = 'module')
def movie():
    return '000|엑시트|한국|2019|2018'

@pytest.fixture(scope = 'module')
def watcha():
    site = crawler.read_site('watcha')
    return site

@pytest.fixture(scope = 'module')
def naver():
    site = crawler.read_site('naver_movie')
    return site

@pytest.fixture(scope = 'module')
def daum():
    site = crawler.read_site('daum_movie')
    return site

@pytest.fixture(scope = 'module')
def maxmovie():
    site = crawler.read_site('maxmovie')
    return site

@pytest.fixture(scope = 'module')
def header():
    return crawler.get_header()

def test_get_url_watcha(watcha, movie):
    watcha_url = 'https://watcha.com/ko-KR/contents/mdErj22'
    url = crawler.get_url(watcha, movie )
    assert watcha_url == url

def test_get_url_naver(naver, movie):
    naver_url = 'https://movie.naver.com/movie/bi/mi/basic.nhn?code=174903'
    url = crawler.get_url(naver, movie)
    assert naver_url == url

def test_get_url_daum(daum, movie):
    daum_url = 'http://movie.daum.net/moviedb/main?movieId=121137'
    url = crawler.get_url(daum, movie)
    assert daum_url == url

def test_get_url_maxmovie(maxmovie, movie):
    maxmovie_url = 'https://www.maxmovie.com/Movie/M000106709'
    url = crawler.get_url(maxmovie, movie)
    assert maxmovie_url == url

# poster는 후에 모듈 수정 시 검증 방법을 달리함
def test_getdata_watcha(watcha, header):
    import requests
    from lxml import html
    watcha_url = 'https://watcha.com/ko-KR/contents/mdErj22'

    page = requests.get(watcha_url, headers = header)
    tree = html.fromstring(page.content)

    score_xpath = watcha['score_xpath']
    score = crawler.get_score(tree, score_xpath)
    assert score

    actor_xpath = watcha['actor_xpath']
    actor = crawler.get_actor(tree, actor_xpath)
    assert score

    poster_xpath = watcha['poster_xpath']
    poster = crawler.get_poster(tree, poster_xpath)
    assert poster

    summary_xpath = watcha['summary_xpath']
    summary = crawler.get_summary(tree, summary_xpath)
    assert summary

def test_getdata_naver(naver, header):
    import requests
    from lxml import html
    naver_url = 'https://movie.naver.com/movie/bi/mi/basic.nhn?code=174903'

    page = requests.get(naver_url, headers = header)
    tree = html.fromstring(page.content)

    score_xpath = naver['score_xpath']
    score = crawler.get_score(tree, score_xpath)
    assert score

    actor_xpath = naver['actor_xpath']
    actor = crawler.get_actor(tree, actor_xpath)
    assert score

    poster_xpath = naver['poster_xpath']
    poster = crawler.get_poster(tree, poster_xpath)
    assert poster

    summary_xpath = naver['summary_xpath']
    summary = crawler.get_summary(tree, summary_xpath)
    assert summary

def test_getdata_daum(daum, header):
    import requests
    from lxml import html
    daum_url = 'http://movie.daum.net/moviedb/main?movieId=121137'

    page = requests.get(daum_url, headers = header)
    tree = html.fromstring(page.content)

    score_xpath = daum['score_xpath']
    score = crawler.get_score(tree, score_xpath)
    assert score

    actor_xpath = daum['actor_xpath']
    actor = crawler.get_actor(tree, actor_xpath)
    assert score

    poster_xpath = daum['poster_xpath']
    poster = crawler.get_poster(tree, poster_xpath)
    assert poster

    summary_xpath = daum['summary_xpath']
    summary = crawler.get_summary(tree, summary_xpath)
    assert summary

def test_getdata_maxmovie(maxmovie, header):
    import requests
    from lxml import html
    maxmovie_url = 'https://www.maxmovie.com/Movie/M000106709'

    page = requests.get(maxmovie_url, headers = header)
    tree = html.fromstring(page.content)

    score_xpath = maxmovie['score_xpath']
    score = crawler.get_score(tree, score_xpath)
    assert score

    actor_xpath = maxmovie['actor_xpath']
    actor = crawler.get_actor(tree, actor_xpath)
    assert score

    poster_xpath = maxmovie['poster_xpath']
    poster = crawler.get_poster(tree, poster_xpath)
    assert poster

    summary_xpath = maxmovie['summary_xpath']
    summary = crawler.get_summary(tree, summary_xpath)
    assert summary
