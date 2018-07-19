import urllib
import requests
from requests import exceptions

import time
import os
import re
import socket


class Bing:
    def __init__(self):
        self.URL = 'http://cn.bing.com/images/async'
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/56.0.2924.87 Safari/537.36',
                        'Referer': 'https://cn.bing.com/images/'}

    def getPicURL(self, searchWord, pn):
        params = {
                  'q': searchWord,
                  'first':str(36*int(pn)),
                  'count':'35',
                  'relp':'35',
                  'mmasync':'1',
                  }
        try:
            print('geting')
            response = requests.get(self.URL, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
        except exceptions.Timeout as e:
            print(e.message)
        except exceptions.HTTPError as e:
            print(e.message)
        except Exception as e:
            print('something wrong!')
            raise Exception
        else:
            urls = re.findall('src="(http:.*?)"', response.text)
            return urls

    def download_one_image(self, urls, save_file_name):
        socket.setdefaulttimeout(15)
        try:
            urllib.request.urlretrieve(urls, save_file_name)
        except socket.timeout:
            return 0
        return 0
       
    def startCrawler(self, searchWord):
        page_max = 1
        if not os.path.isdir(searchWord):
            try:
                os.mkdir(searchWord)
            except OSError:
                print('there is a file named '+searchWord+'!!!!')
                exit()

        for i in range(0, page_max):
            try:
                urls = self.getPicURL(searchWord, i)
                if len(urls) >= 35:
                    print(urls[0])
                    self.download_one_image(urls[0],'test.jpg')
                    time.sleep(5)
                else:
                    return 0
            except Exception as e:
                print(e)


if __name__ == '__main__':
    test = Bing()
    test.startCrawler('dog')
