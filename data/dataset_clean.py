import pandas as pd
df=pd.read_csv("dataset.csv")
print(df.head())
print(df.tail())
print(df.info())
print(df.isnull())
print(df.isnull().sum())
print(df[df.album_name.isnull()])
print(df.drop(65900,inplace=True))
print(df.isnull().sum())
df1=pd.read_csv("spotify_scrap.csv")
print(df1.head())
print(df1.isnull().sum())
print(df1.info())


