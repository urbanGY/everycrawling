import pytest
import everycrawling

@pytest.fixture(scope = 'module')
def movie():
    return '000|엑시트|한국|2019|2018'

@pytest.fixture(scope = 'module')
def watcha():
    site = everycrawling.read_site('watcha')
    return site

@pytest.fixture(scope = 'module')
def naver():
    site = everycrawling.read_site('naver_movie')
    return site

@pytest.fixture(scope = 'module')
def daum():
    site = everycrawling.read_site('daum_movie')
    return site

@pytest.fixture(scope = 'module')
def maxmovie():
    site = everycrawling.read_site('maxmovie')
    return site


def test_get_url_watcha(watcha, movie):
    watcha_url = 'https://watcha.com/ko-KR/contents/mdErj22'
    url = everycrawling.get_url(watcha, movie)
    assert watcha_url == url

def test_get_url_naver(naver, movie):
    naver_url = 'https://movie.naver.com/movie/bi/mi/basic.nhn?code=174903'
    url = everycrawling.get_url(naver, movie)
    assert naver_url == url

def test_get_url_daum(daum, movie):
    daum_url = 'http://movie.daum.net/moviedb/main?movieId=121137'
    url = everycrawling.get_url(daum, movie)
    assert daum_url == url

def test_get_url_maxmovie(maxmovie, movie):
    maxmovie_url = 'https://www.maxmovie.com/Movie/M000106709'
    url = everycrawling.get_url(maxmovie, movie)
    assert maxmovie_url == url
