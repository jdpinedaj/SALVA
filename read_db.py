import pandas as pd
import psycopg2
import constants
from sqlalchemy import create_engine, text
 
#Connection info
POSTGRES_ADDRESS = constants.POSTGRES_ADDRESS ## INSERT YOUR DB ADDRESS
POSTGRES_PORT = constants.POSTGRES_PORT
POSTGRES_USERNAME = constants.POSTGRES_USERNAME ## CHANGE THIS TO YOUR POSTGRES USERNAME
POSTGRES_PASSWORD = constants.POSTGRES_PASSWORD ## CHANGE THIS TO YOUR POSTGRES PASSWORD 
POSTGRES_DBNAME = constants.POSTGRES_DBNAME ## CHANGE THIS TO YOUR DATABASE NAME

# Create the connection
postgres_str = "postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}".format(
    username=POSTGRES_USERNAME,
    password=POSTGRES_PASSWORD,
    ipaddress=POSTGRES_ADDRESS,
    port=POSTGRES_PORT,
    dbname=POSTGRES_DBNAME,
)

cnx = create_engine(postgres_str)

def runQuery(sql):
    result = cnx.connect().execute((text(sql)))
    return pd.DataFrame(result.fetchall(), columns=result.keys())

def getCon():
    return cnx