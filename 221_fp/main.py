
import statistics

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

def readFile(fileName):
    contents = []
    f = open(fileName, encoding='latin-1')
    contents = f.read()
    f.close()
    return contents

def main():
    date_sentiments = []

    for i in range(1,5):
        filePath = "./data/train/GOOGL/" + str(i)
        lines = readFile(filePath)
        sentiment = sia.polarity_scores(lines)['compound']
        date_sentiments.append(sentiment)
        print("Sentiment " + str(i) + ": \t" + str(sentiment))
    overall_sentiment = statistics.mean(date_sentiments)
    if overall_sentiment > 0:
        print("Your requested stock will increase!")
    elif overall_sentiment < 0:
        print("Your requested stock will decrease!")
    else:
        print("Your requested stock will be stable")




if __name__ == "__main__":
        main()
