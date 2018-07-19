from spider.spider import Spider
import re


class Beike(Spider):

    def getInfo(self, list_one):
        title = re.findall("<div class=\"title\">(.+?)</div>", list_one)[0]
        title = re.findall("<a.+?</a>", title)[0]
        title = re.findall(">(.+?)<", title)[0]

        houseInfo = re.findall("<div class=\"houseInfo\">(.+?)</div>", list_one)[0]
        link = re.findall("href=\"(.+?)\"", houseInfo)[0]
        disc = houseInfo.split("</a>")[1]
        houseInfo = {"link": link, "discrip": disc}

        totalPrice = re.findall("<div class=\"totalPrice\">(.+?)</div>", list_one)[0]
        totalPrice = re.findall("<span>(.+?)</span>", totalPrice)[0]

        unitPrice = re.findall("<div class=\"unitPrice\".+?</div>", list_one)[0]
        unitPrice = re.findall("<span>(.+?)</span>", unitPrice)[0]

        ret = {
            "title": title,
            "houseInfo": houseInfo,
            "totalPrice": totalPrice,
            "unitPrice": unitPrice
        }
        return ret

    def getList(self, text):
        ret = []
        ul = re.findall("<ul class=\"sellListContent\".+?</ul>", text)
        if not len(ul) == 0:
            li = re.findall("<li.+?</li>", ul[0])
            ret = [self.getInfo(list_one) for list_one in li]
        return ret
