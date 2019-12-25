MAPBOXTOKEN = #Your Mapbox token
GOOGLEROUTESKEY = #Your google route api key
DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
HOURS = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","21","23"]
LOCALDATAPATH = 'localdata/'
finaldatasetsproject11/'
SQLCOORD = """select * from public.gral_accidents where (substr(fecha,0,5)||substr(fecha,6,2)||substr(fecha,9)) between '2014-01-01' and '2016-12-31'"""
SQLGRAL = """select * from public.stg_coord_accidents where (substr(fecha_homologada,0,5)||substr(fecha_homologada,6,2)||substr(fecha_homologada,9)) between '2014-01-01' and '2016-12-31'"""
LOGO='salva-logo.png'
POSTGRES_ADDRESS = #Your own
POSTGRES_PORT = #Your own
POSTGRES_USERNAME = #Your own
POSTGRES_PASSWORD = #Your own
POSTGRES_DBNAME = #Your own

HEATMAPSTYLE='Magma'
REVERSECOLORSCALE=True
MODEL='model/RFC_model11.sav'


TYPE_ACCIDENT= {0: 'Atropello', 1: 'Caida Ocupante', 2: 'Choque', 3: 'Otro', 4: 'Volcamiento'}
TYPE_ROAD={0: 'Ciclo Ruta', 1: 'Glorieta', 2: 'Interseccion', 3: 'Lote o Predio', 4: 'None', 5: 'Paso Elevado', 6: 'Paso Inferior', 7: 'Tramo de via', 8: 'Via peatonal', 9: 'via troncal', 10: 'Tunel'}
CLIMATE={0: 'Lluvia', 1: 'Niebla', 2: 'None', 3: 'Normal', 4: 'Viento'}
STREET_USE={0: 'Doble Sentido', 1: 'Otro', 2: 'Un Sentido'}
NUMBER_ROADS={0: 'Dos', 1: 'Otro', 2: 'Uno'}
NUMBER_LANES={0: 'Dos', 1: 'Otro', 2: 'Tres', 3: 'Uno'}
ROLLING_SURFACE={0: 'Otro', 1: 'Pavimentado'}
STATUS_ROAD={0: 'Bueno', 1: 'Malo', 2: 'Otro'}
HUMIDITY={0: 'Humeda', 1: 'Otro', 2: 'Seca'}
ILLUMINATION={0: 'Buena', 1: 'Mala', 2: 'Otro'}
TRAFFIC_LIGHT={0: 'Bueno', 1: 'Malo', 2: 'Otro'}
VERTICAL_SIGNALS={0: 'Bueno', 1: 'Malo', 2: 'Otro'}
HORIZONTAL_SIGNALS={0: 'Bueno', 1: 'Malo', 2: 'Otro'}
SPEED_BREAKERS={0: 'No', 1: 'Si'}
STREET_LINES={0: 'No', 1: 'Si'}
VISIBILITY={0: 'Buena', 1: 'Mala', 2: 'Otro'}
