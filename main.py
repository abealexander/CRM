# Import Packages
from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
import os
from flask_cors import CORS, cross_origin
from loan_default.prediction_Validation_Insertion import pred_validation
from loan_default.trainingModel import trainModel
from loan_default.training_Validation_Insertion import train_validation
from loan_default.predictFromModel import prediction
import json
# Hardik
# from Database_operations.MongoDB_operations import MongoDB_operation

# Define flask app
app = Flask(__name__)
CORS(app)

# Render Home page
@app.route('/', methods=['GET'])
@cross_origin()
def get_home():
    return(render_template('Home.html'))

# Render About & Help page
# @app.route('/about_help', methods=["GET"])
# @cross_origin()
# def get_about_help():
#     return(render_template('about_help.html'))

# Loan Default
@app.route("/intelligence/loan_default/predict", methods=['POST'])
@cross_origin()
def predictRouteClient():
    try:
        if request.json is not None:
            path = request.json['folderPath']

            pred_val = pred_validation(path) #object initialization

            pred_val.prediction_validation() #calling the prediction_validation function

            pred = prediction(path) #object initialization

            # predicting for dataset present in database
            path,json_predictions = pred.predictionFromModel()
            return Response("Prediction File created at !!!"  +str(path) +'and few of the predictions are '+str(json.loads(json_predictions) ))
        elif request.form is not None:
            path = request.form['folderPath']

            pred_val = pred_validation(path) #object initialization

            pred_val.prediction_validation() #calling the prediction_validation function

            pred = prediction(path) #object initialization

            # predicting for dataset present in database
            path,json_predictions = pred.predictionFromModel()
            return Response("Prediction File created at !!!"  +str(path) +'and few of the predictions are '+str(json.loads(json_predictions) ))
        else:
            print('Nothing Matched')
    except ValueError:
        return Response("Error Occurred! %s" %ValueError)
    except KeyError:
        return Response("Error Occurred! %s" %KeyError)
    except Exception as e:
        return Response("Error Occurred! %s" %e)

@app.route("/intelligence/loan_default/train", methods=['POST'])
@cross_origin()
def trainRouteClient():

    try:
        if request.json['folderPath'] is not None:
            path = request.json['folderPath']

            train_valObj = train_validation(path) #object initialization

            train_valObj.train_validation() #calling the training_validation function


            trainModelObj = trainModel() #object initialization
            trainModelObj.trainingModel() #training the model for the files in the table

    except ValueError:

        return Response("Error Occurred! %s" % ValueError)

    except KeyError:

        return Response("Error Occurred2! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred! %s" % e)
    return Response("Training successfull!!")

# Hardik
@app.route('/intelligence/sentiment')
def upload_file():
   return render_template('test_upload_html.html')

@app.route('/intelligence/sentiment/uploader', methods=['GET', 'POST'])
def upload_file_():
    if request.method == 'POST':
        file = request.files['file']
        # df = pd.read_csv(file, encoding = 'latin1')
        mongo = MongoDB_operation(DB_name='Sentiment_DB', collection_name='New_Data')
        mongo.InsertData(csv_file=file)

        # print(df.head(3))
        return "File upload Successful!!"

# Run app
if __name__ == '__main__':
    app.run(debug=True)