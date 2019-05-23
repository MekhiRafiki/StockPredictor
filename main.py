
import statistics
from urllib.request import urlopen
import re
from bs4 import BeautifulSoup

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
SENTIMENT_BOUNDARY = 0

def readFile(fileName):
    contents = []
    f = open(fileName, encoding='latin-1')
    contents = f.read()
    f.close()
    return contents


def articleParser(article_page):
    soup = BeautifulSoup(article_page, features="html.parser")
    text = soup.find_all('article')
    if len(text) > 0:
        text = text[0].get_text()
        sentiment = sia.polarity_scores(text)['compound']
        return sentiment
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

def yahooFinanceParser(companySymbol):
    visitedUrls = set()
    page = urlopen('https://finance.yahoo.com/quote/' + companySymbol + '/news/').read()
    relevant_articles = articleUrlParser(page)
    sentiments = []
    for articleUrl in relevant_articles:
        url = "https://finance.yahoo.com/" + articleUrl
        visitedUrls.add(url)
        try:
            article_page = urlopen(url).read()
        except:
            print("Couldn't open one of the links")
            print(articleUrl)
        sentiment = articleParser(article_page)
        if sentiment != None:
            sentiments.append(sentiment)
            print(articleUrl + " Sentiment " + ": \t" + str(sentiment))
    sum = 0
    for rating in sentiments:
        if rating < SENTIMENT_BOUNDARY:
            sum += 1
        elif rating < SENTIMENT_BOUNDARY:
            sum -= 1
    overall_sentiment = statistics.mean(sentiments)
    return (visitedUrls, overall_sentiment, sum)


def main():
    companySymbol = "TSLA"
    afterYahoo = yahooFinanceParser(companySymbol)
    visitedSet = afterYahoo[0]
    overall_sentiment = afterYahoo[1]
    abs = afterYahoo[2]
    print(abs)
    if overall_sentiment > 0:
        print("Your requested stock will increase!")
    elif overall_sentiment < 0:
        print("Your requested stock will decrease!")
    else:
        print("Your requested stock will be stable")
    print(visitedSet)
    #print(relevant_articles)







if __name__ == "__main__":
        main()
