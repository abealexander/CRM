from datetime import datetime
from loan_default.Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
from loan_default.DataTypeValidation_Insertion_Prediction.DataTypeValidationPrediction import dBOperation
from loan_default.DataTransformation_Prediction.DataTransformationPrediction import dataTransformPredict
from loan_default.application_logging import logger

class pred_validation:
    def __init__(self,path):
        self.raw_data = Prediction_Data_validation(path)
        self.dataTransform = dataTransformPredict()
        self.dBOperation = dBOperation()
        self.file_object = open("loan_default/Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()

    def prediction_validation(self):

        try:

            self.log_writer.log(self.file_object,'Start of Validation on files for prediction!!')
            #extracting values from prediction schema
            column_names_NumberofColumns = self.raw_data.valuesFromSchema()
            #getting the regex defined to validate filename
            regex = self.raw_data.manualRegexCreation()
            #validating filename of prediction files
            self.raw_data.validationFileNameRaw(regex)
            #validating column length in the file
            self.raw_data.validateColumnLength(column_names_NumberofColumns[8:16])
            #validating if any column has all values missing
            self.raw_data.validateMissingValuesInWholeColumn()
            self.log_writer.log(self.file_object,"Raw Data Validation Complete!!")

            self.log_writer.log(self.file_object,("Starting Data Transforamtion!!"))
            #replacing blanks in the csv file with "Null" values to insert in table
            self.dataTransform.replaceMissingWithNull()

            self.log_writer.log(self.file_object,"DataTransformation Completed!!!")

            self.log_writer.log(self.file_object,"Creating Prediction_Database and Collections and Insertion of Data into Collection!!!!!!")
            # create database with given name, if present open the connection! Create collections and insert csv files in the collections
            self.dBOperation.insertIntoCollectionGoodData('Prediction')
            self.log_writer.log(self.file_object, "Collection created and Data Insertion Completed!!")
            self.log_writer.log(self.file_object, "Deleting Good Data Folder!!!")
            #Delete the good data folder after loading files in table
            self.raw_data.deleteExistingGoodDataTrainingFolder()
            self.log_writer.log(self.file_object,"Good_Data folder deleted!!!")
            self.log_writer.log(self.file_object,"Moving bad files to Archive and deleting Bad_Data folder!!!")
            #Move the bad files to archive folder
            self.raw_data.moveBadFilesToArchiveBad()
            self.log_writer.log(self.file_object,"Bad files moved to archive!! Bad folder Deleted!!")
            self.log_writer.log(self.file_object,"Validation Operation completed!!")
            self.log_writer.log(self.file_object,"Extracting csv file from table")
            #export data in table to csvfile
            self.dBOperation.selectingDatafromtableintocsv('Prediction')

        except Exception as e:
            raise e









