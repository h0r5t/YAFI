from urllib.request import urlopen
import csv
import codecs
import YAFIObjects

class YAFIApiWrapper:

    def __init__(self):
        return

    def getCurrentStockPrice(self, symbol):
        URL1 = "http://finance.yahoo.com/d/quotes.csv?s="
        URL2 = "&f=snat1"
        csv_dict = self.getCSVDictForApiCall(URL1 + symbol + URL2)
        price_obj = YAFIObjects.YAFIObjectCurrentStockPrice(csv_dict[0])
        return price_obj

    def getCSVDictForApiCall(self, url):

        response = urlopen(url)
        text = response.read().decode('utf8')
        split = text.split(',')

        dict1 = {}
        counter = 0
        dict1[0] = []
        for element in split:
            if "\n" in element:
                newline_split = element.split("\n")
                dict1[counter].append(newline_split[0])
                if newline_split[1] == "":
                    break
                else:
                    dict1[counter+1] = []
                    dict1[counter+1].append(newline_split[1])
                    counter += 1
            else:
                dict1[counter].append(element)

        return(dict1)
