from joblib import load
import pandas as pd

import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")


filename = 'finalized_google_playstore.sav'
loaded_model = load(filename)

gps_df = pd.read_csv('dataset/google-play-store-apps/googleplaystore.csv')
gps_df.dropna(inplace = True)

column_names = ['Category', 'Content Rating', 'Android Ver', 'Type', 'Size', 'Installs', 'Price', 'Reviews', 'Last Updated']
X = gps_df[column_names].copy()
y = gps_df['Rating'].copy()


a = loaded_model.predict(X.iloc[[1]])

print("*********************************")
print(y.iloc[[1]])
print(a)
print("*********************************")

########################################################################################################################################


filename = 'finalized_google_playstore_for_installs.sav'
loaded_model = load(filename)


column_names = ['Category', 'Content Rating', 'Android Ver', 'Size', 'Price', 'Reviews', 'Rating', 'Last Updated']
X = gps_df[column_names].copy()
y = gps_df['Installs'].copy()

a = loaded_model.predict(X.iloc[[1]])

print("*********************************")
print(y.iloc[[1]])
print(a)
print("*********************************")

filename = 'finalized_google_playstore_for_reviews.sav'
loaded_model = load(filename)


column_names = ['Category', 'Content Rating', 'Android Ver', 'Size', 'Installs', 'Price', 'Rating', 'Last Updated']
X = gps_df[column_names].copy()
y = gps_df['Reviews'].copy()

a = loaded_model.predict(X.iloc[[1]])

print("*********************************")
print(y.iloc[[1]])
print(a)
print("*********************************")