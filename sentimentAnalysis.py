
import statistics
from urllib.request import Request, urlopen
import re
from bs4 import BeautifulSoup
import datetime
from dateutil import parser
import requests
import json

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
SENTIMENT_BOUNDARY = 0
MAX_NASDAQ_PAGES = 5

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

#Nasdaq Specific webscrapping
def nasdaqArticleSentiment(article_page):
    soup = BeautifulSoup(article_page, features="html.parser")
    date = None
    text = soup.find("div", {"id": "articleText"})
    dateTime = soup.find("span", {"itemprop": "datePublished"})
    dateTime = str(dateTime)
    if len(dateTime) > 0:
        date = re.search('"datePublished">(.*)<', dateTime, re.IGNORECASE)
        if date:
            date = date.group(1)
    if text != None and len(text) > 0:
        text = text.get_text()
        sentiment = sia.polarity_scores(text)['compound']
        return (sentiment, date)
    else:
        return None

def nasdaqArticleUrlParser(page):
    soup = BeautifulSoup(page, features="html.parser")
    relevant_articles = []
    links = soup.find_all('a')
    urls = [link.get('href') for link in links]
    newsArticles = [url for url in urls if '/article/' in url]
    return newsArticles

def nasdaqParser(companySymbol, companyDict, visitedURLS):
    relevant_articles = []
    for i in range(1,MAX_NASDAQ_PAGES):
        if i == 1:
            url = 'https://www.nasdaq.com/symbol/'+ companySymbol + '/news-headlines'
        else:
            url = 'https://www.nasdaq.com/symbol/'+ companySymbol + '/news-headlines?page=' + str(i)
        page = urlopen(url).read()
        links = nasdaqArticleUrlParser(page)
        relevant_articles = relevant_articles + links

    #uniq_count = 0
    for articleUrl in relevant_articles:
        url = articleUrl
        try:
            article_page = urlopen(url).read()
        except:
            print("Couldn't open one of the links")
            print(articleUrl)
        parsedArticleData = nasdaqArticleSentiment(article_page)
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
            #uniq_count += 1
    #print("Uniq additions: " + str(uniq_count))
    return companyDict


SOURCES_URL = 'https://newsapi.org/v2/everything?'
auth_API_KEY ='4600336f9f7e4419ac7d586cfbb745bf'

def newsAPI_Sentiment(article_page):
    soup = BeautifulSoup(article_page, features="html.parser")
    date = None
    all_p = soup.find_all('p')
    text = ""
    for p in all_p:
        text += str(p)
    if text != None and len(text) > 0:
        sentiment = sia.polarity_scores(text)['compound']
        return sentiment
    else:
        return None

def newsAPIParser(companyDict, visitedURLS, stockName = "Google", from_date = '2019-05-20', to_date ='2019-06-02'):
    url = (''+SOURCES_URL +
            'q='+stockName+'&'+
            'from='+from_date.isoformat()+'&'+
            'to='+to_date.isoformat()+'&'+
            'sortBy=popularity&'
            'apiKey='+auth_API_KEY
            )
    response = requests.get(url)
    response_json = response.json()
    if 'articles' not in response_json:
        print(response_json['status'])
        print(response_json['code'])
        print(response_json['message'])

    articles = response_json['articles']
    links = []
    for item in articles:
        links.append(item['url'])

    # Sentiment Analyzer
    for articleUrl in links:
        if articleUrl not in visitedURLS:
            url = articleUrl
            try:
                article_page = urlopen(url).read()
            except:
                print("Couldn't open one of the links")
                print(articleUrl)
            page = urlopen(url).read()
            sentiment = newsAPI_Sentiment(page)
            dt = to_date

            newVal = (articleUrl, sentiment)
            if dt in companyDict:
                companyDict[dt].append(newVal)
            else:
                companyDict[dt] = [newVal]

            visitedURLS.add(articleUrl)
    return companyDict

def computeAvgSentiment(companyDict, latestDate):
    absSentiment = 0
    avgSentiment = 0
    validArticleCount = 0
    for date in companyDict:
        if date >= latestDate:
            for articleSentiment in companyDict[date]:
                if articleSentiment[1] > SENTIMENT_BOUNDARY:
                    absSentiment += 1
                elif articleSentiment[1] < SENTIMENT_BOUNDARY:
                    absSentiment -= 1
                avgSentiment += articleSentiment[1]
                validArticleCount +=1
    if validArticleCount == 0:
        overall_sentiment = 0
    else:
        overall_sentiment = avgSentiment / validArticleCount
    return (absSentiment, overall_sentiment, validArticleCount)

def sentimentAnalysis(companySymbol, companyName, latestDate, endDate, companyDict = {}):
    visitedURLS = set()
    if companyDict == {}:
        yahooFinanceParser(companySymbol, companyDict, visitedURLS)
        print("Finished Yahoo")
        nasdaqParser(companySymbol, companyDict, visitedURLS)
        print("Finished NasDaq")

    # NewsAPI Plan restriction
    endDate = datetime.datetime.now()
    restriction_date = endDate.replace(year = endDate.year, month=endDate.month-1, day = endDate.day)
    if latestDate >= restriction_date:
        #newsAPIParser(companyDict, visitedURLS, companyName, latestDate, endDate)
        1+1
    #print("Finished newsAPI")

    #googleFinanceParser(companySymbol, companyDict, visitedURLS)
    sentiment = computeAvgSentiment(companyDict, latestDate)
    absSentiment = sentiment[0]
    overall_sentiment = sentiment[1]
    articleCount = sentiment[2]
    #print("Based on article sentiment since " + str(latestDate) + " on " + str(articleCount) + " articles")
    #print("Absolute: " + str(absSentiment) + '\t' + "Overall Sentiment: " + str(overall_sentiment))

    return (overall_sentiment, articleCount, companyDict)

    #if overall_sentiment > 0:
    #    print("Your requested stock will increase!")
    #elif overall_sentiment < 0:
    #    print("Your requested stock will decrease!")
    #else:
    #    print("Your requested stock will be stable")

    #print(relevant_articles)

def getSentiment(companySymbol, companyName, latestDate, endDate, companyDict):
    return sentimentAnalysis(companySymbol, companyName, latestDate, endDate, companyDict)

def main():
    companySymbol = "GOOGL"
    latestDate = datetime.datetime(2019, 5, 26)
    endDate = datetime.datetime.now()
    sentimentAnalysis(companySymbol, "Google", latestDate, endDate)




if __name__ == "__main__":
        main()
