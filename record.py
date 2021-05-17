from os import path
from datetime import datetime as dt
import requests as rq
import schedule
import time
import pandas as pd

urlGeoJSON = "https://download.data.grandlyon.com/wfs/rdata?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=jcd_jcdecaux.jcdvelov&outputFormat=application/json;%20subtype=geojson&SRSNAME=EPSG:4171&startIndex=0"

def record(fileName):

    print(dt.now())
    print(">>> Requête API")
    reponse = rq.get(urlGeoJSON)
    print(">>> Requête API terminée")
    print(">>> Réponse server HTTP :",reponse)
    time.sleep(2)

    if reponse.status_code == 200:
        dataGeoJSON = reponse.json()
        print(">>> Normalisation")
        data = pd.json_normalize(dataGeoJSON['features'])
        data['time'] = dt.now()
        print(">>> Normalisation terminée")
        time.sleep(2)

        print(">>> Enregistrement")
        if path.exists(f'{fileName}'):
            data.to_csv(f'{fileName}',sep = ',', mode = 'a', header = False)
        else:
            data.to_csv(f'{fileName}',sep = ',', mode = 'a')
        print(">>> Enregistrement terminé")
        time.sleep(2)

        print(dt.now(),'\n')

now = dt.now().replace(microsecond = 0)
fileName = 'Desktop/Velo_v/records/' + dt.strftime(now,'%Y-%m-%d %H:%M:%S')[5:-3].replace(':','h') + '.csv'

schedule.clear()
schedule.every().minutes.at(':00').do(record,fileName)
print(">>> Fichier :",fileName,'\n')
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print('\n>>> Parsing terminé')
    print('>>> Fichier :',fileName)