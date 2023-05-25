import pandas as pd
import string
import re
import spacy
from spacy.lang.es.stop_words import STOP_WORDS
import tqdm
import numpy as np

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

nlp = spacy.load("../model/model-best")
REGX_USERNAME = r"@[A-Za-z0-9$-_@.&+]+"

def preprocessing(text):
  text = text.lower()
  text = re.sub(REGX_USERNAME, ' ', text)
  tokens = [token.text for token in nlp(text)]
  tokens = [t for t in tokens if t not in STOP_WORDS and t not in string.punctuation and len(t) > 2]
  tokens = [t for t in tokens if not t.isdigit()]

  return " ".join(tokens)

def get_polarity(df):

    for i in tqdm.tqdm(range(len(df)), desc="Getting polarity"):
        try:
            doc = nlp(preprocessing(df.iloc[i]['Mensaje']))

            # doc.cats = {'POS': a, 'NEG': b}

            df.at[i, 'polarity'] = doc.cats['POS'] - doc.cats['NEG']
        
        except:
            df.at[i, 'polarity'] = 0

    return df

def analyze_spacy(input):

    df = whatsapp_to_df(input)
    
    df['polarity'] = np.nan
    df['neg'] = np.nan
    df['neu'] = np.nan
    df['pos'] = np.nan

    get_polarity(df)

    # We return the dataframe
    return df