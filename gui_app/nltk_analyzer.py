import nltk
import pandas as pd
import numpy as np
import tqdm
import random
import matplotlib


nltk.download('vader_lexicon') # Obligatorio para usar SentimentIntensityAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()


def corregir_palabras(corrector, palabras, agregarPrimero=[]):   
    #codificacion = corrector.get_dic_encoding()   # obtenemos la codificacion para usarla luego

    # agregamos las palabras aleatorias al diccionario
    for palabra in agregarPrimero:
        corrector.add(palabra)

    # autocorreccion de palabras
    corregida = []
    for p in palabras:
        ok = corrector.spell(p)   # verificamos ortografia
        if not ok:
            sugerencias = corrector.suggest(p)
            if len(sugerencias) > 0:  # hay sugerencias
                # tomamos la  mejor sugerencia(decodificada a string)
                mejor_sugerencia = sugerencias[0]   
                corregida.append(mejor_sugerencia)
            else:
                corregida.append(p)  # no hay ninguna sugerecia para la palabra
        else:
            corregida.append(p)   # esta palabra esta corregida

    return corregida


def corregir_oracion(corrector,string):
    oracion_fixed=''
    if len(string)>0:
        oracion_dirty=string.split()
        oracion_fixed=corregir_palabras(corrector, oracion_dirty,[''])
        oracion_fixed=' '.join(oracion_fixed)
    else:
      print('error')
    return oracion_fixed

def preprocess(ReviewText):
    ReviewText = ReviewText.str.replace('\t', ' ')
    ReviewText = ReviewText.str.replace('\r', ' ')
    ReviewText = ReviewText.str.replace('\n', ' ')
    return (ReviewText)

def get_polarity(df):
  for i in tqdm.tqdm(range(len(df)), desc="Getting polarity"):
      try:
          temp=df['Mensaje'][i]
          p=sid.polarity_scores(str(temp))['compound']
          neg=sid.polarity_scores(str(temp))['neg']
          neu=sid.polarity_scores(str(temp))['neu']
          pos=sid.polarity_scores(str(temp))['pos']
          df.loc[i,'polarity']=p
          df.loc[i,'neg']=neg
          df.loc[i,'neu']=neu
          df.loc[i,'pos']=pos
          #sleep(0.1+random.random()/2) # Already translated
      except Exception as e:
          print('Error {}:{}'.format(i,e))


def whatsapp_to_df(path):

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Creamos un dataframe con las columnas que necesitamos
    df = pd.DataFrame(columns=['Fecha', 'Hora', 'Usuario', 'Mensaje'])

    # Los mensajes de whatsapp tienen un formato de fecha y hora, y luego el nombre del usuario y el mensaje
    # Ejemplo: 9/11/22, 03:49 - Usuario: Mensaje

    # Iteramos sobre las lineas del archivo
    for line in tqdm.tqdm(lines, desc="Reading file"):
        # Separamos la linea en fecha, hora, usuario y mensaje
        try:
            datetime, usermsg = line.split(' - ')
            date, time = datetime.split(', ')
            user, msg = usermsg.split(': ')

            # Eliminamos los saltos de linea del mensaje
            msg = msg.replace('\n', '')

            # Agregamos una nueva fila al dataframe
            df.loc[len(df)] = [date, time, user, msg]

        except:
            # We found a line that doesn't follow the format, so we add it to the last message
            df.loc[len(df)-1, 'Mensaje'] += line
    
    return df


## ANALISIS DE SENTIMIENTO ##

def analyze_nltk(input):

    df = whatsapp_to_df(input)
    
    df['polarity'] = np.nan
    df['neg'] = np.nan
    df['neu'] = np.nan
    df['pos'] = np.nan

    get_polarity(df)

    # We return the dataframe
    return df