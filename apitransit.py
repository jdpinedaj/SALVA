import googlemaps
import constants
from datetime import datetime
import pickle

gmaps = googlemaps.Client(key=constants.GOOGLEROUTESKEY)

# Geocoding an address


def geocode_address(addresstext):
    return gmaps.geocode(addresstext)

# Look up an address with reverse geocoding


def reverse_geocode_result(lat, lon):
    return gmaps.reverse_geocode((lat, lon))


# Request directions via public transit
#now = datetime.now()


def directions_result(addfrom, addto, tmode):
    return gmaps.directions(addfrom,
                            addto,
                            mode=tmode,
                            departure_time=datetime.now())


#=========================================
# Function for getting the nearby clusters
# Similar to the one explained By Meraldo Antonio in: 
#https://github.com/meraldoantonio/AccidentPredictor/blob/master/CODE/Exploratory%20Data%20Analysis/UK_Accidents_Google_Route_Predict.ipynb
#=========================================
from math import sin, cos, sqrt, atan2, radians
kms_per_radian = 6371.0088
# Dataframe with cluster columns coords as latitude and longitude, and target dataframe 
# Return Cluster -1 as default if no result with weight 0.
def getClusters(df_cluster, y ,x,distance, df_eval):
    R=kms_per_radian
    df_eval['Cluster'] = -1
    df_eval['Weight'] = float(0.000000)
    lats = df_eval[y]
    longs = df_eval[x]
    for i in range(0,df_eval.shape[0]):
        for j in range(0,df_cluster.shape[0]):
            cluster_id = int (df_cluster.iloc[[j]]['Cluster'])
            lat1 = radians(float(df_cluster.iloc[[j]][y]))
            lon1 = radians(float(df_cluster.iloc[[j]][x]))
            lat2 = radians(lats[i])
            lon2 = radians(longs[i])

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c

            if(distance < 0.080):
                print("Result: [Cluster " + str(cluster_id) + "]: " + str(distance*1000) + " m")
                df_eval.at[i,'Weight']= (df_cluster.iloc[[j]]['Weight'])
                df_eval.at[i,'Cluster']= int(df_cluster.iloc[[j]]['Cluster'])
    return df_eval



#=========================================
# Function for predicting severity of accidents 
#=========================================
RFC_model11 = constants.MODEL
model = pickle.load(open(RFC_model11, 'rb'))

def predict_severity(values):
    new_params_to_predict = values.reshape(1,9)
    proba_new_values = model.predict_proba(new_params_to_predict)
    return(round(proba_new_values[0][1]*100, 2))