import pandas as pd
import os
import glob

class Data_Getter_Pred:
    """
    This class shall  be used for obtaining the data from the source for prediction.

    """
    def __init__(self, file_object, logger_object):
        self.prediction_filepath='loan_default/Prediction_FileFromDB/'
        self.file_object=file_object
        self.logger_object=logger_object

    def get_data(self):
        """
        Method Name: get_data
        Description: This method reads the data from source.
        Output: A pandas DataFrame.
        On Failure: Raise Exception

        """
        self.logger_object.log(self.file_object,'Entered the get_data method of the Data_Getter class')
        try:
            self.all_filepath = glob.glob(os.path.join(self.prediction_filepath, "*.csv")) # list of filepaths
            self.file_name = []
            for file in self.all_filepath:
                self.file_name.append(os.path.splitext(os.path.basename(file))[0]) # Getting the file name without extension
            for name, file_path in zip(self.file_name, self.all_filepath):
                globals()[f"prediction{name}"] = pd.read_csv(file_path) # Reading the file content to create a DataFrame
            self.logger_object.log(self.file_object,'Data Load Successful.Exited the get_data method of the Data_Getter class')
            return predictionAccounts, predictionCards, predictionClients, predictionDisps, predictionDistricts, predictionLoans, predictionOrders, predictionTransactions
        except Exception as e:
            self.logger_object.log(self.file_object,'Exception occured in get_data method of the Data_Getter class. Exception message: '+str(e))
            self.logger_object.log(self.file_object,
                                   'Data Load Unsuccessful.Exited the get_data method of the Data_Getter class')
            raise Exception()


