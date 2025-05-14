import requests
import json
import pandas as pd


def groupe_predominant(liste_codes):
    """Détermine le groupe prédominant dans une liste de codes météo.

    Args:
        liste_codes (list): Une liste d'entiers représentant les codes météo.

    Returns:
        str: Le nom du groupe prédominant, ou None s'il y a une égalité.
    """

    df = pd.DataFrame()
    compteur = {}
    weather_conditions = {
            "2xx": "Thunderstorm",
            "3xx": "Drizzle",
            "5xx": "Rain",
            "6xx": "Snow",
            "7xx": "Atmosphere",
            "800": "Clear",
            "80x": "Clouds"
        }

    # Compter les occurrences de chaque groupe
    for code in liste_codes:
        if code == 800:
            groupe = "800"
        elif code//10 == 80:
            groupe = "80x"
        else:
            groupe = code // 100
            groupe = str(groupe) + "xx"

        compteur[groupe] = compteur.get(groupe, 0) + 1

    # Trouver le groupe avec le plus grand nombre d'occurrences
    max_occurrences = max(compteur.values())
    groupes_max = [groupe for groupe, occ in compteur.items() if occ == max_occurrences]

    # return [group for group in groupes_max]
    return groupes_max[0]

def get_daily_index_ranges(df):
  """
  Extracts the first and last index of each day from a DataFrame 
  with a 'dt_txt_date' column.

  Args:
    df: The input DataFrame.

  Returns:
    A dictionary where keys are dates and values are tuples 
    containing the first and last index for that day.
  """

  df['dt_txt_date'] = pd.to_datetime(df['dt_txt_date']) 
  daily_index_ranges = {}
  i_day = 0

  for date, group in df.groupby('dt_txt_date'):
    first_index = group.index[0]
    last_index = group.index[-1]
    daily_index_ranges[(i_day)] = (first_index, last_index)
    i_day += 1

  return daily_index_ranges


if __name__ == "__main":
    # Création d'une' liste
    city_list = ["Mont Saint Michel",
    "St Malo",
    "Bayeux",
    "Le Havre",
    "Rouen",
    "Paris",
    "Amiens",
    "Lille",
    "Strasbourg",
    "Chateau du Haut Koenigsbourg",
    "Colmar",
    "Eguisheim",
    "Besancon",
    "Dijon",
    "Annecy",
    "Grenoble",
    "Lyon",
    "Gorges du Verdon",
    "Bormes les Mimosas",
    "Cassis",
    "Marseille",
    "Aix en Provence",
    "Avignon",
    "Uzes",
    "Nimes",
    "Aigues Mortes",
    "Saintes Maries de la mer",
    "Collioure",
    "Carcassonne",
    "Ariege",
    "Toulouse",
    "Montauban",
    "Biarritz",
    "Bayonne",
    "La Rochelle"]

    # Création d'un dictionaire
    dict_city = {}

    ###################################### GPS ######################################

    # Récupération des coordonnées GPS
    # Scraping des coordonnées  des villes
    url_api = "https://nominatim.openstreetmap.org/search?"
    headers = {'User-Agent': 'MonApplicationGeocodage/1.0 (contact: marcellin.stephane@gmail.com)'}

    for city in city_list:
        payload = {"city":city, "format": "json"}
        r = requests.get(url=url_api, params=payload, headers=headers)
        if r.status_code == 200:
            data = json.loads(r.text)
            if data:
                latitude = data[0]['lat']
                longitude = data[0]['lon']
                dict_city[city] = (latitude,longitude)
            else:
                dict_city[city] = (666,666)

    ###################################### METEO ######################################

    # Récupération des données météo de chaque ville

    coord_df = pd.DataFrame()
    weather_df = pd.DataFrame()
    main_df = pd.DataFrame()
    wind_df = pd.DataFrame()
    clouds_df = pd.DataFrame()
    sys_df = pd.DataFrame()

    df_current = pd.DataFrame()
    df_forecast = pd.DataFrame()

    # Définition des urls et de l'API key
    url_api_current_weather = "https://api.openweathermap.org/data/2.5/weather?"
    url_api_forecast_weather = "https://api.openweathermap.org/data/2.5/forecast?"
    API_Key = "21baaf834c0cf582a9c57ddf0f955212"

    for city, gps in dict_city.items():
        payload = {"lat":gps[0], "lon": gps[1],"appid": API_Key, "lang": "fr", "units": "metric"}

        r_current = requests.get(url=url_api_current_weather, params=payload)
        if r_current.status_code == 200:
            data_current = json.loads(r_current.text)
            if data_current:
                # Extraire les données des sous-dictionnaires
                df = pd.DataFrame(data_current, index=[0]) 

                df['city'] = city

                df['weather_main'] = df['weather'][0]['main']
                df['weather_description'] = df['weather'][0]['description']
                df['weather_icon'] = df['weather'][0]['icon']
                df = df.drop('weather', axis=1)

                # Flatten 'coord', 'main', 'wind' and 'sys' 
                for key in ['coord', 'main', 'wind', 'sys']:
                    for subkey in data_current[key]:
                        df[f'{key}_{subkey}'] = data_current[key][subkey]
                    df = df.drop(key, axis=1)

                df_current = pd.concat([df_current, df], axis =0, ignore_index=True)

        r_forecast = requests.get(url=url_api_forecast_weather, params=payload)
        if r_forecast.status_code == 200:
            data_forecast = json.loads(r_forecast.text)
            if data_forecast:
                cnt = int(data_forecast['cnt'])

                # Extraire les données des sous-dictionnaires
                df1 = pd.DataFrame() 
                df1['city'] = [city]
            

                for i_cnt in range(cnt):
                    idata_forecast = data_forecast['list'][i_cnt]     # Dictionnaire avec le timestamps n°i_cnt
                    df1['dt'] = idata_forecast['dt']
                

                    df1['temperature'] = idata_forecast['main']['temp']
                    df1['temperature_max'] = idata_forecast['main']['temp_max']
                    df1['temperature_min'] = idata_forecast['main']['temp_min']

                    df1['weather'] = idata_forecast['weather'][0]['main']
                    df1['weather_id'] = idata_forecast['weather'][0]['id']

                    df1[['dt_txt_date','dt_txt_time']] = idata_forecast['dt_txt'].split()

                    df1['Precipitation_prob'] = idata_forecast['pop']

                    df_forecast = pd.concat([df_forecast, df1], axis =0, ignore_index=True)

    # Recherche de la meilleur ville
    weather_notation = {
            "2xx": -10, #"Thunderstorm",
            "3xx": -2, #"Drizzle",
            "5xx": -5, #"Rain",
            "6xx": -5, #"Snow",
            "7xx": 0,#"Atmosphere",
            "800": 10,#"Clear",
            "80x": 0,#"Clouds"
        }
    tendance_5jours = {}

    # Calcul du score de chaque ville ne fonction du dictionnaire précédent

    for city in dict_city:
        # Création dataframe
        df_city = pd.DataFrame()
        
        previsions_city_score = 0

        # Creation d'un mask pour extraire les données d'une ville
        mask = df_forecast["city"] == city
        df_city = df_forecast.loc[mask,:].reset_index(drop=True)

        # On récupère les index pour isoler chaque jour
        index = get_daily_index_ranges(df_city)
        


        # On regarde la tendance globale par jour
        for idx in range(5):
            value = groupe_predominant(df_city.loc[:,"weather_id"].iloc[index[idx][0]:index[idx][1]+1])
            previsions_city_score += weather_notation[value]

        tendance_5jours[str(city)] = previsions_city_score

    df_score = pd.DataFrame.from_dict( tendance_5jours, orient='index', columns = ['Score'])
    city_win, score_win = max(tendance_5jours.items(), key=lambda item: item[1])
    
            


