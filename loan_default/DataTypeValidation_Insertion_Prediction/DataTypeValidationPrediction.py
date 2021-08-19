import shutil
import json
import pandas as pd
import pymongo
import glob
from datetime import datetime
from os import listdir
import os
from loan_default.application_logging.logger import App_Logger


class dBOperation:
    """
          This class shall be used for handling all the SQL operations.

          """

    def __init__(self):
        self.path = 'loan_default/Prediction_Database/'
        self.badFilePath = "loan_default/Prediction_Raw_Files_Validated/Bad_Raw"
        self.goodFilePath = "loan_default/Prediction_Raw_Files_Validated/Good_Raw"
        self.logger = App_Logger()

    def insertIntoCollectionGoodData(self,DatabaseName):

        """
                                       Method Name: insertIntoTableGoodData
                                       Description: This method creates a Database, creates a collection and inserts the Good data files from the Good_Raw folder into the
                                            respective collections.
                                       Output: None
                                       On Failure: Raise Exception

                """

        try:
            client = pymongo.MongoClient(
                "mongodb+srv://abe:abe@cluster0.ifiok.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
            file = open("loan_default/Prediction_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Opened %s database successfully" % DatabaseName)
            file.close()
        except ConnectionError:
            file = open("loan_default/Prediction_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Error while connecting to database: %s" % ConnectionError)
            file.close()
            raise ConnectionError
        try:
            goodFilePath = self.goodFilePath
            badFilePath = self.badFilePath
            log_file = open("loan_default/Prediction_Logs/DbCollectionDataInsertionLog.txt", 'a+')
            goodFilePaths = glob.glob(os.path.join(goodFilePath, "*.csv"))
            collection_names = []
            for file in glob.glob(os.path.join(goodFilePath, "*.csv")):
                collection_names.append(os.path.splitext(os.path.basename(file))[0])
            for collection_name, file_path in zip(collection_names, goodFilePaths):
                db = client[DatabaseName]
                coll = db[collection_name]
                data = pd.read_csv(file_path)
                payload = json.loads(data.to_json(orient='records'))
                coll.remove()
                coll.insert(payload)
            self.logger.log(log_file, " %s: Files loaded successfully!!" % file)
        except Exception as e:
            self.logger.log(log_file, "Error while creating collection and inserting data: %s " % e)
            shutil.move(goodFilePath + '/' + file, badFilePath)
            self.logger.log(log_file, "File Moved Successfully %s" % file)
            log_file.close()
            raise e
        log_file.close()


    def selectingDatafromtableintocsv(self,Database):

        """
                                       Method Name: selectingDatafromtableintocsv
                                       Description: This method exports the data in GoodData table as a CSV file. in a given location.
                                                    above created .
                                       Output: None
                                       On Failure: Raise Exception

                """

        self.fileFromDb = 'loan_default/Prediction_FileFromDB/'
        self.fileName = 'InputFile.csv'
        log_file = open("loan_default/Prediction_Logs/ExportToCsv.txt", 'a+')
        try:
            # Make the CSV output directory
            if not os.path.isdir(self.fileFromDb):
                os.makedirs(self.fileFromDb)

            client = pymongo.MongoClient(
                "mongodb+srv://abe:abe@cluster0.ifiok.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")  # To be changed as per requirement
            db = client[Database]
            collection_names = db.collection_names()
            for collection_name in collection_names:
                coll = db[collection_name]
                df = pd.DataFrame(list(coll.find()))
                df.drop('_id', axis=1, inplace=True)
                df.to_csv(self.fileFromDb + collection_name + ".csv", index=False)

            self.logger.log(log_file, "File exported successfully!!!")
            log_file.close()
        except Exception as e:
            self.logger.log(log_file, "File exporting failed. Error : %s" %e)
            raise e





