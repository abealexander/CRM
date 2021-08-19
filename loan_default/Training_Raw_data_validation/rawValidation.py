from datetime import datetime
from os import listdir
import os
import glob
import re
import json
import shutil
import pandas as pd
from loan_default.application_logging.logger import App_Logger





class Raw_Data_validation:

    """
             This class shall be used for handling all the validation done on the Raw Training Data!!.

             """

    def __init__(self,path):
        self.Raw_File_Directory = path
        self.schema_path = 'loan_default/schema_training/'
        self.logger = App_Logger()


    def valuesFromSchema(self):
        """
                        Method Name: valuesFromSchema
                        Description: This method extracts all the relevant information from the pre-defined "Schema" file.
                        Output: column_names, Number of Columns
                        On Failure: Raise ValueError,KeyError,Exception

                                """
        try:
            self.schema_filepath = glob.glob(os.path.join(self.schema_path, "*.json"))  # list of schema filepaths
            self.schema_name = []
            for schema in self.schema_filepath:
                self.schema_name.append(os.path.splitext(os.path.basename(schema))[0]) # Getting the schema filename without extension
            for schema_name, schema_filepath in zip(self.schema_name, self.schema_filepath):
                with open(schema_filepath, 'r') as f:
                    dic = json.load(f)
                    f.close()
                    globals()[f"column_names_{schema_name}"] = dic['ColName']
                    globals()[f"NumberofColumns_{schema_name}"] = dic['NumberofColumns']

            file = open("loan_default/Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            message = "NumberofColumns_accounts_training:: %s" %NumberofColumns_accounts_training + "\n" + "NumberofColumns_cards_training:: %s" %NumberofColumns_cards_training + "\n" + "NumberofColumns_clients_training:: %s" %NumberofColumns_clients_training + "\n"+ "NumberofColumns_disps_training:: %s" %NumberofColumns_disps_training + "\n"+ "NumberofColumns_districts_training:: %s" %NumberofColumns_districts_training + "\n"+ "NumberofColumns_loans_training:: %s" %NumberofColumns_loans_training + "\n"+ "NumberofColumns_orders_training:: %s" %NumberofColumns_orders_training + "\n"+ "NumberofColumns_transactions_training:: %s" %NumberofColumns_transactions_training + "\n"
            self.logger.log(file,message)
            file.close()

        except ValueError:
            file = open("loan_default/Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file,"ValueError:Value not found inside schema_training")
            file.close()
            raise ValueError

        except KeyError:
            file = open("loan_default/Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file, "KeyError:Key value error incorrect key passed")
            file.close()
            raise KeyError

        except Exception as e:
            file = open("loan_default/Training_Logs/valuesfromSchemaValidationLog.txt", 'a+')
            self.logger.log(file, str(e))
            file.close()
            raise e

        return column_names_accounts_training, column_names_cards_training, column_names_clients_training, column_names_disps_training, column_names_districts_training, column_names_loans_training, column_names_orders_training, column_names_transactions_training, NumberofColumns_accounts_training, NumberofColumns_cards_training, NumberofColumns_clients_training, NumberofColumns_disps_training, NumberofColumns_districts_training, NumberofColumns_loans_training, NumberofColumns_orders_training, NumberofColumns_transactions_training


    def manualRegexCreation(self):
        """
                                Method Name: manualRegexCreation
                                Description: This method contains a manually defined regex based on the "FileName" given in "Schema" file.
                                            This Regex is used to validate the filename of the training data.
                                Output: Regex pattern
                                On Failure: None

                                        """
        regex = "[A-Za-z]+\.csv"
        return regex

    def createDirectoryForGoodBadRawData(self):

        """
                                      Method Name: createDirectoryForGoodBadRawData
                                      Description: This method creates directories to store the Good Data and Bad Data
                                                    after validating the training data.

                                      Output: None
                                      On Failure: OSError

                                              """

        try:
            path = os.path.join("loan_default/Training_Raw_files_validated/", "Good_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)
            path = os.path.join("loan_default/Training_Raw_files_validated/", "Bad_Raw/")
            if not os.path.isdir(path):
                os.makedirs(path)

        except OSError as ex:
            file = open("loan_default/Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file,"Error while creating Directory %s:" % ex)
            file.close()
            raise OSError

    def deleteExistingGoodDataTrainingFolder(self):

        """
                                            Method Name: deleteExistingGoodDataTrainingFolder
                                            Description: This method deletes the directory made  to store the Good Data
                                                          after loading the data in the table. Once the good files are
                                                          loaded in the DB,deleting the directory ensures space optimization.
                                            Output: None
                                            On Failure: OSError

                                                    """

        try:
            path = 'loan_default/Training_Raw_files_validated/'
            # if os.path.isdir("ids/" + userName):
            # if os.path.isdir(path + 'Bad_Raw/'):
            #     shutil.rmtree(path + 'Bad_Raw/')
            if os.path.isdir(path + 'Good_Raw/'):
                shutil.rmtree(path + 'Good_Raw/')
                file = open("loan_default/Training_Logs/GeneralLog.txt", 'a+')
                self.logger.log(file,"GoodRaw directory deleted successfully!!!")
                file.close()
        except OSError as s:
            file = open("loan_default/Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file,"Error while Deleting Directory : %s" %s)
            file.close()
            raise OSError

    def deleteExistingBadDataTrainingFolder(self):

        """
                                            Method Name: deleteExistingBadDataTrainingFolder
                                            Description: This method deletes the directory made to store the bad Data.
                                            Output: None
                                            On Failure: OSError

                                                    """

        try:
            path = 'loan_default/Training_Raw_files_validated/'
            if os.path.isdir(path + 'Bad_Raw/'):
                shutil.rmtree(path + 'Bad_Raw/')
                file = open("loan_default/Training_Logs/GeneralLog.txt", 'a+')
                self.logger.log(file,"BadRaw directory deleted before starting validation!!!")
                file.close()
        except OSError as s:
            file = open("loan_default/Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file,"Error while Deleting Directory : %s" %s)
            file.close()
            raise OSError

    def moveBadFilesToArchiveBad(self):

        """
                                            Method Name: moveBadFilesToArchiveBad
                                            Description: This method deletes the directory made  to store the Bad Data
                                                          after moving the data in an archive folder. We archive the bad
                                                          files to send them back to the client for invalid data issue.
                                            Output: None
                                            On Failure: OSError

                                                    """
        now = datetime.now()
        date = now.date()
        time = now.strftime("%H%M%S")
        try:

            source = 'loan_default/Training_Raw_files_validated/Bad_Raw/'
            if os.path.isdir(source):
                path = "loan_default/TrainingArchiveBadData"
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = 'loan_default/TrainingArchiveBadData/BadData_' + str(date)+"_"+str(time)
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                files = os.listdir(source)
                for f in files:
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)
                file = open("loan_default/Training_Logs/GeneralLog.txt", 'a+')
                self.logger.log(file,"Bad files moved to archive")
                path = 'loan_default/Training_Raw_files_validated/'
                if os.path.isdir(path + 'Bad_Raw/'):
                    shutil.rmtree(path + 'Bad_Raw/')
                self.logger.log(file,"Bad Raw Data Folder Deleted successfully!!")
                file.close()
        except Exception as e:
            file = open("loan_default/Training_Logs/GeneralLog.txt", 'a+')
            self.logger.log(file, "Error while moving bad files to archive:: %s" % e)
            file.close()
            raise e




    def validationFileNameRaw(self,regex):
        """
                    Method Name: validationFileNameRaw
                    Description: This function validates the name of the training csv files as per given name in the schema!
                                 Regex pattern is used to do the validation.If name format do not match the file is moved
                                 to Bad Raw Data folder else in Good raw data.
                    Output: None
                    On Failure: Exception

                """

        #pattern = "[A-Za-z]+\.csv"
        # delete the directories for good and bad data in case last run was unsuccessful and folders were not deleted.
        self.deleteExistingBadDataTrainingFolder()
        self.deleteExistingGoodDataTrainingFolder()
        #create new directories
        self.createDirectoryForGoodBadRawData()
        onlyfiles = [f for f in listdir(self.Raw_File_Directory)]
        try:
            f = open("loan_default/Training_Logs/nameValidationLog.txt", 'a+')
            for filename in onlyfiles:
                if (re.match(regex, filename)):
                    shutil.copy("loan_default/Training_Raw_Files/" + filename, "loan_default/Training_Raw_files_validated/Good_Raw")
                    self.logger.log(f,"Valid File name!! File moved to GoodRaw Folder :: %s" % filename)

                else:
                    shutil.copy("loan_default/Training_Raw_Files/" + filename, "loan_default/Training_Raw_files_validated/Bad_Raw")
                    self.logger.log(f,"Invalid File Name!! File moved to Bad Raw Folder :: %s" % filename)

            f.close()

        except Exception as e:
            f = open("loan_default/Training_Logs/nameValidationLog.txt", 'a+')
            self.logger.log(f, "Error occured while validating FileName %s" % e)
            f.close()
            raise e




    def validateColumnLength(self,NumberofColumns):
        """
                          Method Name: validateColumnLength
                          Description: This function validates the number of columns in the csv files.
                                       It is should be same as given in the schema file.
                                       If not same file is not suitable for processing and thus is moved to Bad Raw Data folder.
                                       If the column number matches, file is kept in Good Raw Data for processing.
                                      The csv file is missing the first column name, this function changes the missing name to "Wafer".
                          Output: None
                          On Failure: Exception

                           Written By: iNeuron Intelligence
                          Version: 1.0
                          Revisions: None

                      """
        try:
            f = open("loan_default/Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f,"Column Length Validation Started!!")
            i=0
            for file in listdir('loan_default/Training_Raw_files_validated/Good_Raw/'):
                csv = pd.read_csv("loan_default/Training_Raw_files_validated/Good_Raw/" + file)
                if csv.shape[1] == NumberofColumns[i]:
                    pass
                else:
                    shutil.move("loan_default/Training_Raw_files_validated/Good_Raw/" + file, "loan_default/Training_Raw_files_validated/Bad_Raw")
                    self.logger.log(f, "Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)
                i+=1
            self.logger.log(f, "Column Length Validation Completed!!")
        except OSError:
            f = open("loan_default/Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            f.close()
            raise OSError
        except Exception as e:
            f = open("loan_default/Training_Logs/columnValidationLog.txt", 'a+')
            self.logger.log(f, "Error Occured:: %s" % e)
            f.close()
            raise e
        f.close()

    def validateMissingValuesInWholeColumn(self):
        """
                                  Method Name: validateMissingValuesInWholeColumn
                                  Description: This function validates if any column in the csv file has all values missing.
                                               If all the values are missing, the file is not suitable for processing.
                                               SUch files are moved to bad raw data.
                                  Output: None
                                  On Failure: Exception

                              """
        try:
            f = open("loan_default/Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f,"Missing Values Validation Started!!")

            for file in listdir('loan_default/Training_Raw_files_validated/Good_Raw/'):
                csv = pd.read_csv("loan_default/Training_Raw_files_validated/Good_Raw/" + file)
                count = 0
                for columns in csv:
                    if (len(csv[columns]) - csv[columns].count()) == len(csv[columns]):
                        count+=1
                        shutil.move("loan_default/Training_Raw_files_validated/Good_Raw/" + file,
                                    "loan_default/Training_Raw_files_validated/Bad_Raw")
                        self.logger.log(f,"Invalid Column Length for the file!! File moved to Bad Raw Folder :: %s" % file)
                        break
                if count==0:
                    csv.rename(columns={"Unnamed: 0": "Wafer"}, inplace=True)
                    csv.to_csv("loan_default/Training_Raw_files_validated/Good_Raw/" + file, index=None, header=True)
        except OSError:
            f = open("loan_default/Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f, "Error Occured while moving the file :: %s" % OSError)
            f.close()
            raise OSError
        except Exception as e:
            f = open("loan_default/Training_Logs/missingValuesInColumn.txt", 'a+')
            self.logger.log(f, "Error Occured:: %s" % e)
            f.close()
            raise e
        f.close()
