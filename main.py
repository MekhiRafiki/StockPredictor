import numpy as np
import regression
import sentimentAnalysis as SA
import datetime

class NeuralNetwork():

    def __init__(self):
        # seeding for random number generation
        np.random.seed(1)

        #converting weights to a 3 by 1 matrix with values from -1 to 1 and mean of 0
        self.synaptic_weights = 2 * np.random.random((3, 1)) - 1

    def sigmoid(self, x):
        #applying the sigmoid function
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        #computing derivative to the Sigmoid function
        return x * (1 - x)

    def train(self, training_inputs, training_outputs, training_iterations):

        #training the model to make accurate predictions while adjusting weights continually
        for iteration in range(training_iterations):
            #siphon the training data via  the neuron
            output = self.think(training_inputs)


            #computing error rate for back-propagation
            error = training_outputs - output

            #performing weight adjustments
            adjustments = np.dot(training_inputs.T, error * self.sigmoid_derivative(output) * 10)
            self.synaptic_weights += adjustments
            #print("Weights after Adjustments: ", self.synaptic_weights)


    def think(self, inputs):
        #passing the inputs via the neuron to get output
        #converting values to floats

        inputs = inputs.astype(float)
        output = self.sigmoid(np.dot(inputs, self.synaptic_weights))
        return output



def main(companyName, companySymbol):
    #initializing the neuron class

    neural_network = NeuralNetwork()

    print("Beginning Randomly Generated Weights: ")
    print(neural_network.synaptic_weights)

    #training data consisting of 4 examples--3 input values and 1 output
    training_examples = []
    training_examples_outputs = []
    companyDict = {}  # Avoid Slowdown from Yahoo and Nasdaq during training. Cache the results

    for i in range(1, 13):
        example = []
        # set up dates
        latestDate = datetime.datetime(2018, i, 1)
        if i == 12:
            endDate = datetime.datetime(2019, 1, 1)
        else:
            endDate = datetime.datetime(2018, i+1, 1)
        sentiment_analysis_tuple = SA.getSentiment(companySymbol, companyName, latestDate, endDate, companyDict)
        example.append(sentiment_analysis_tuple[0])
        example.append(float(sentiment_analysis_tuple[1]/100))
        companyDict = sentiment_analysis_tuple[2]

        while True:
            try:
                regression_tuple = regression.main(companySymbol, endDate)
                if regression_tuple[1] == None:
                    print('No data for {}. Trying the next market day'.format(endDate.isoformat()))
                    endDate = endDate.replace(year = endDate.year, month=endDate.month, day = endDate.day+1)
                else:
                    break
            except:
                print('Markets were closed on {}. Trying the next day this month'.format(endDate.isoformat()))
                endDate = endDate.replace(year = endDate.year, month=endDate.month, day = endDate.day+1)

        #print(regression_tuple)
        example.append(regression_tuple[0])
        training_examples_outputs.append(regression_tuple[1])  #truth value

        training_examples.append(example)
    training_inputs = np.array(training_examples)
    #print(training_inputs)

    #training_inputs = np.array([[0,0,1],
    #                            [1,1,1],
    #                            [1,0,1],
    #                            [0,1,1]])
    #print(training_examples_outputs)
    training_outputs = np.array([training_examples_outputs]).T
    #training_outputs = np.array([[0,1,1,0]]).T

    #training taking place
    neural_network.train(training_inputs, training_outputs, 15000)

    print("Ending Weights After Training: ")
    print(neural_network.synaptic_weights)
    pred_date = datetime.datetime(2019, 5, 13)
    pred_back = pred_date.replace(year = pred_date.year, month=pred_date.month-1, day = pred_date.day)

    input_features = []
    sentiment_analysis_tuple = SA.getSentiment(companySymbol, companyName, pred_back, pred_date, companyDict)
    #print(sentiment_analysis_tuple)
    input_features.append(sentiment_analysis_tuple[0])
    input_features.append(float(sentiment_analysis_tuple[1]/100))
    #print(sentiment_analysis_tuple[1])
    regression_tuple = regression.main(companySymbol, pred_date)
    input_features.append(regression_tuple[0])

    actual = regression_tuple[1]

    print("Considering New Situation: " + str(input_features))
    print("New Output data: ")
    print("Prediction: ", neural_network.think(np.array(input_features)))
    print("Actual Change: ", actual)
    print("Wow, we did it!")

if __name__ == "__main__":
    companyName = str(input("Input Company Name: "))
    companySymbol = str(input("Input Company Symbol: "))
    main(companyName, companySymbol)
