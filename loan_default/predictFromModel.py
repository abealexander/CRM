import pandas as pd
from loan_default.file_operations import file_methods
from loan_default.data_preprocessing import preprocessing
from loan_default.data_ingestion import data_loader_prediction
from loan_default.application_logging import logger
from loan_default.Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
import os


class prediction:

    def __init__(self,path):
        self.file_object = open("loan_default/Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()
        if path is not None:
            self.pred_data_val = Prediction_Data_validation(path)

    def predictionFromModel(self):

        try:
            self.pred_data_val.deletePredictionFile() #deletes the existing prediction file from last run!
            self.log_writer.log(self.file_object,'Start of Prediction')
            data_getter=data_loader_prediction.Data_Getter_Pred(self.file_object,self.log_writer)
            predictionAccounts, predictionCards, predictionClients, predictionDisps, predictionDistricts, predictionLoans, predictionOrders, predictionTransactions =data_getter.get_data()

            preprocessor = preprocessing.Preprocessor(self.file_object,self.log_writer)

            # Merging Loan and Accounts table
            predictData = pd.merge(predictionLoans, predictionAccounts, left_on='account_id', right_on='account_id',
                                   how='inner', validate='one_to_one')
            self.log_writer.log(self.file_object, 'Preprocessing of Prediction Data')
            # Parsing Dates to Datetime Format and year extraction
            predictData['account_year'] = pd.to_datetime(predictData['date_y'])
            predictData['account_year'] = predictData['account_year'].dt.year
            # Calculating number of years from account creation and date of loan issuance
            predictData['years_between'] = predictData['grant_year'] - predictData['account_year']
            # Removing columns that doesn't contribute to prediction
            predictData = preprocessor.remove_columns(predictData, ['frequency', 'date_x', 'date_y'])
            # Merging Order to above train data
            average_ord = predictionOrders[['account_id', 'amount']]
            # Calculating average order value pertaining to each account
            average_ord = average_ord.groupby('account_id').mean()
            predictData = predictData.merge(average_ord, left_on='account_id', right_on='account_id', how='left',
                                            validate='one_to_one')
            predictData.rename(columns={'amount_x': 'loan_amount',
                                        'amount_y': 'avg_order_amt'}, inplace=True)
            predictData.fillna(0, inplace = True)
            self.log_writer.log(self.file_object, 'Merging Order Data with Train Data')
            # Merging transaction table
            avg_trans_amt = predictionTransactions[['account_id', 'transaction_amount', 'current_balance']]
            # Calculating average balance and average transaction account
            avg_trans_amt = avg_trans_amt.groupby('account_id').mean()
            predictData = predictData.merge(avg_trans_amt, left_on='account_id', right_on='account_id', how='inner',
                                            validate='one_to_one')
            self.log_writer.log(self.file_object, 'Merging Transaction Data with Train Data')
            # Calculating number of transaction by each account and merging it to predictData
            n_transaction = predictionTransactions.groupby('account_id')['transaction_type'].count().reset_index()
            n_transaction = n_transaction.rename({'transaction_type': 'n_transaction'}, axis=1)
            # Merging number of transaction done by each account who have loans sanctioned
            predictData = predictData.merge(n_transaction, left_on='account_id', right_on='account_id', how='inner',
                                            validate='one_to_one')
            self.log_writer.log(self.file_object, 'Merging Volume of Transactions with Train Data')
            # Merging district dataset
            dist = predictionDistricts.merge(predictionAccounts, left_on='district_id', right_on='district_id',
                                             how='left',
                                             validate='one_to_many')
            dist = dist[['account_id', 'No_of_Inhabitants', 'Average_Salary', 'Unemployment_rate_1995',
                         'Unemployment_rate_1996', 'Crimes_commited_in_1995', 'Crimes_commited_in_1996']]
            # Creating new column for avg unemployment rate by adding unemployment rate of 1995 and 1996 and dividing it by 2
            dist['Avg_unemployement_rate'] = (dist['Unemployment_rate_1995'] + dist['Unemployment_rate_1996']) / 2
            # Creating new column for avg crime rate by adding crimes commited of both year, dividing it by number of inhabitants and finally dividing it by 2'''
            dist['Avg_crime_rate'] = ((dist['Crimes_commited_in_1995'] + dist['Crimes_commited_in_1996']) / (
                    2 * dist['No_of_Inhabitants']))
            dist = preprocessor.remove_columns(dist, ['Unemployment_rate_1995', 'Unemployment_rate_1996',
                                                      'Crimes_commited_in_1995', 'Crimes_commited_in_1996'])
            # merging above district dataset to train data
            predictData = predictData.merge(dist, left_on='account_id', right_on='account_id', how='inner',
                                            validate='one_to_one')
            self.log_writer.log(self.file_object, 'Merging District Data with Train Data')

            file_loader = file_methods.File_Operation(self.file_object, self.log_writer)
            kmeans = file_loader.load_model('KMeans')

            ##Code changed
            #pred_data = predictData.drop(['account_id'], axis=1) # drops the first column for cluster prediction
            clusters = kmeans.predict(predictData)
            predictData['clusters'] = clusters
            clusters = predictData['clusters'].unique()

            for i in clusters:
                cluster_data = predictData[predictData['clusters'] == i]
                label_name = list(cluster_data['account_id'])
                cluster_data = predictData.drop(labels=['account_id'], axis=1)
                cluster_data = cluster_data.drop(['clusters'], axis=1)
                model_name = file_loader.find_correct_model_file(i)
                model = file_loader.load_model(model_name)
                result = list(model.predict(cluster_data))
                result = pd.DataFrame(list(zip(label_name, result)), columns=['account_id', 'Prediction'])

                outname = 'Prediction.csv'

                outdir = 'loan_default/Prediction_Output_file'
                if not os.path.exists(outdir):
                    os.mkdir(outdir)

                fullname = os.path.join(outdir, outname)

                result.to_csv(fullname,header=True,mode='a+')

            self.log_writer.log(self.file_object, 'End of Prediction')
        except Exception as ex:
            self.log_writer.log(self.file_object, 'Error occured while running the prediction!! Error:: %s' % ex)
            raise ex
        return fullname, result.head().to_json(orient="records")


