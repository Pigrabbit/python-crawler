import requests
from bs4 import BeautifulSoup

def getPageString(uri):
    data = requests.get(uri, headers={
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    })
    bs_obj = BeautifulSoup(data.content, "html.parser")

    print(bs_obj.find_all('ul', attrs={"class":"baby-product-list"}))
    return data.content

uri = "https://www.coupang.com/np/categories/194282?page=1"
getPageString(uri)
