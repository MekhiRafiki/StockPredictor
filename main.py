
import statistics
from urllib.request import Request, urlopen
import re
from bs4 import BeautifulSoup
import datetime
from dateutil import parser

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
SENTIMENT_BOUNDARY = 0

def readFile(fileName):
    contents = []
    f = open(fileName, encoding='latin-1')
    contents = f.read()
    f.close()
    return contents


def articleSentimentParser(article_page):
    soup = BeautifulSoup(article_page, features="html.parser")
    date = None
    text = soup.find_all('article')
    dateTime = soup.find_all('time')
    if len(dateTime) > 0:
        date = dateTime[0]['datetime'][:10]
    if len(text) > 0:
        text = text[0].get_text()
        sentiment = sia.polarity_scores(text)['compound']
        return (sentiment, date)
    else:
        return None

def articleUrlParser(page):
    soup = BeautifulSoup(page, features="html.parser")
    relevant_articles = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href[:6] == "/news/":
            relevant_articles.append(href) #rhef
    return relevant_articles

def yahooFinanceParser(companySymbol, companyDict, visitedURLS):
    page = urlopen('https://finance.yahoo.com/quote/' + companySymbol + '/news/').read()
    relevant_articles = articleUrlParser(page)
    sentiments = []
    for articleUrl in relevant_articles:
        url = "https://finance.yahoo.com/" + articleUrl
        try:
            article_page = urlopen(url).read()
        except:
            print("Couldn't open one of the links")
            print(articleUrl)
        parsedArticleData = articleSentimentParser(article_page)
        if parsedArticleData != None:
            sentiment = parsedArticleData[0]
            date = parsedArticleData[1]
            dt = parser.parse(date)
            newVal = (url, sentiment)
            if dt in companyDict:
                companyDict[dt].append(newVal)
            else:
                companyDict[dt] = [newVal]
            visitedURLS.add(url)
    return companyDict

# Two functions below are under development
# Google finds many ways to block webscrapers

def googleArticleUrlParser(page):
    soup = BeautifulSoup(page, features="html.parser")
    relevant_articles = []
    print(soup.find_all("a"))

def googleFinanceParser(companySymbol, companyDict, visitedURLS):
    url = 'https://www.google.com/search?q='+ companySymbol + '&tbm=fin'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    googleArticleUrlParser(page)


def computeAvgSentiment(companyDict, latestDate):
    absSentiment = 0
    avgSentiment = 0
    validArticleCount = 0
    for date in companyDict:
        if date >= latestDate:
            for articleSentiment in companyDict[date]:
                if articleSentiment[1] < SENTIMENT_BOUNDARY:
                    absSentiment += 1
                elif articleSentiment[1] < SENTIMENT_BOUNDARY:
                    absSentiment -= 1

                avgSentiment += articleSentiment[1]
                validArticleCount +=1
    overall_sentiment = avgSentiment / validArticleCount   #statistics.mean(avgSentiment)
    return (absSentiment, overall_sentiment)


def main():
    companySymbol = "TSLA"
    companyDict = {}
    visitedURLS = set()
    yahooFinanceParser(companySymbol, companyDict, visitedURLS)
    #googleFinanceParser(companySymbol, companyDict, visitedURLS)
    latestDate = datetime.datetime(2019, 5, 20)
    sentiment = computeAvgSentiment(companyDict, latestDate)
    absSentiment = sentiment[0]
    overall_sentiment = sentiment[1]
    print("Based on article sentiment since " + str(latestDate))
    print("Absolute: " + str(absSentiment) + '\t' + "Overall Sentiment: " + str(overall_sentiment))

    if overall_sentiment > 0:
        print("Your requested stock will increase!")
    elif overall_sentiment < 0:
        print("Your requested stock will decrease!")
    else:
        print("Your requested stock will be stable")
    #print(relevant_articles)







if __name__ == "__main__":
        main()
