from spider.spider import Spider

class Comic(Spider):
    def test(self):
        print('test')
if __name__ == '__main__':
    c=Comic()
    c.test()