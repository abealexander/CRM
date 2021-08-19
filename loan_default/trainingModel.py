
# Doing the necessary imports
import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from loan_default.data_ingestion import data_loader
from loan_default.data_preprocessing import preprocessing
from loan_default.data_preprocessing import clustering
from loan_default.best_model_finder import tuner
from loan_default.file_operations import file_methods
from loan_default.application_logging import logger

#Creating the common Logging object


class trainModel:

    def __init__(self):
        self.log_writer = logger.App_Logger()
        self.file_object = open("loan_default/Training_Logs/ModelTrainingLog.txt", 'a+')

    def trainingModel(self):
        # Logging the start of Training
        self.log_writer.log(self.file_object, 'Start of Training')
        try:
            # Getting the data from the source
            data_getter=data_loader.Data_Getter(self.file_object,self.log_writer)
            trainAccounts, trainCards, trainClients, trainDisps, trainDistricts, trainLoans, trainOrders, trainTransactions=data_getter.get_data()

            """doing the data preprocessing"""
            self.log_writer.log(self.file_object, 'Start of data preprocessing')
            preprocessor=preprocessing.Preprocessor(self.file_object,self.log_writer)
            # Encoding bad loans as 1 and good loans as -1
            trainLoans['status_desc'] = trainLoans['status_desc'].replace({'Contract finished no problem': -1,
                                                                               'Contract finised, loan was not paid': 1,
                                                                               'Runing contract OK so far': -1,
                                                                               'Runing contract client in debt': 1})
            self.log_writer.log(self.file_object, 'Target Label Encoding')
            # Merging Loan and Account Data to create Train Data
            trainData = pd.merge(trainLoans, trainAccounts, left_on='account_id', right_on='account_id', how='inner', validate='one_to_one')
            self.log_writer.log(self.file_object, 'Creation of Train Data')
            # Parsing Dates to Datetime Format and year extraction
            trainData['account_year'] = pd.to_datetime(trainData['date_y'])
            trainData['account_year'] = trainData['account_year'].dt.year
            # Calculating number of years from account creation and date of loan issuance
            trainData['years_between'] = trainData['grant_year'] - trainData['account_year']
            # Removing columns that doesn't contribute to prediction
            trainData = preprocessor.remove_columns(trainData,['status', 'date_x', 'date_y'])
            # Merging Order to above train data
            average_ord = trainOrders[['account_id', 'amount']]
            # Calculating average order value pertaining to each account
            average_ord = average_ord.groupby('account_id').mean()
            trainData = trainData.merge(average_ord, left_on='account_id', right_on='account_id', how='left',
                                        validate='one_to_one')
            trainData.rename(columns={'amount_x': 'loan_amount',
                                                  'amount_y': 'avg_order_amt'}, inplace=True)
            trainData.fillna(0, inplace=True)
            self.log_writer.log(self.file_object, 'Merging Order Data with Train Data')
            # Merging transaction table
            avg_trans_amt = trainTransactions[['account_id', 'transaction_amount', 'current_balance']]
            # Calculating average balance and average transaction account
            avg_trans_amt = avg_trans_amt.groupby('account_id').mean()
            trainData = trainData.merge(avg_trans_amt, left_on='account_id', right_on='account_id', how='inner',
                                        validate='one_to_one')
            self.log_writer.log(self.file_object, 'Merging Transaction Data with Train Data')
            # Calculating number of transaction by each account and merging it to trainData
            n_transaction = trainTransactions.groupby('account_id')['transaction_type'].count().reset_index()
            n_transaction = n_transaction.rename({'transaction_type': 'n_transaction'}, axis=1)
            # Merging number of transaction done by each account who have loans sanctioned
            trainData = trainData.merge(n_transaction, left_on='account_id', right_on='account_id', how='inner',
                                        validate='one_to_one')
            self.log_writer.log(self.file_object, 'Merging Volume of Transactions with Train Data')
            # Merging district dataset
            dist = trainDistricts.merge(trainAccounts, left_on='district_id', right_on='district_id', how='left',
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
            trainData = trainData.merge(dist, left_on='account_id', right_on='account_id', how='inner',
                                        validate='one_to_one')
            self.log_writer.log(self.file_object, 'Merging District Data with Train Data')
            X = trainData[
                ['loan_id', 'account_id','loan_amount', 'duration', 'payments', 'grant_year', 'district_id', 'tenure',
                 'account_loyalty', 'account_year', 'years_between', 'avg_order_amt',
                 'transaction_amount', 'current_balance', 'n_transaction',
                 'No_of_Inhabitants', 'Average_Salary', 'Avg_unemployement_rate', 'Avg_crime_rate']]
            Y = trainData[['status_desc']]
            sm = SMOTE(sampling_strategy='auto', k_neighbors=5, random_state=10)

            X_res, y_res = sm.fit_resample(X, Y)

            """ Applying the clustering approach"""

            kmeans=clustering.KMeansClustering(self.file_object,self.log_writer) # object initialization.
            number_of_clusters=kmeans.elbow_plot(X_res)  #  using the elbow plot to find the number of optimum clusters

            # Divide the data into clusters
            X=kmeans.create_clusters(X_res,number_of_clusters)

            #create a new column in the dataset consisting of the corresponding cluster assignments.
            X['Labels']=y_res

            # getting the unique clusters from our dataset
            list_of_clusters=X['Cluster'].unique()

            """parsing all the clusters and looking for the best ML algorithm to fit on individual cluster"""
            for i in list_of_clusters:
                cluster_data=X[X['Cluster']==i] # filter the data for one cluster

                # Prepare the feature and Label columns
                cluster_features=cluster_data.drop(['account_id', 'Labels','Cluster'],axis=1)
                cluster_label= cluster_data['Labels']

                # splitting the data into training and test set for each cluster one by one
                x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=1 / 3, random_state=355)

                model_finder=tuner.Model_Finder(self.file_object,self.log_writer) # object initialization

                #getting the best model for each of the clusters
                best_model_name,best_model=model_finder.get_best_model(x_train,y_train,x_test,y_test)

                #saving the best model to the directory.
                file_op = file_methods.File_Operation(self.file_object,self.log_writer)
                save_model=file_op.save_model(best_model,best_model_name+str(i))

            # logging the successful Training
            self.log_writer.log(self.file_object, 'Successful End of Training')
            self.file_object.close()

        except Exception:
            # logging the unsuccessful Training
            self.log_writer.log(self.file_object, 'Unsuccessful End of Training')
            self.file_object.close()
            raise Exception