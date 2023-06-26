from datasets import load_dataset
import pandas as pd
import numpy as np

def get_dataset():
    dataset = dataset = load_dataset("./EmoEvent")
    return dataset

def get_dataframe(dataset):
    df = pd.DataFrame(dataset['train'])
    return df

# we get the dataframe
dataset = get_dataset()
df = get_dataframe(dataset)

# we print the information of the dataframe
print(df.info())

# we print the first 5 rows of the dataframe
print(df.head())

# we pass the dataframe to a csv file
df.to_csv('dataset.csv', index=False)