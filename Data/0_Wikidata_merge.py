import pandas as pd

# merging data
df_cast_1960 = pd.read_pickle("df_cast_1960.pkl")
df_cast_1970 = pd.read_pickle("df_cast_1970.pkl")
df_cast_1980 = pd.read_pickle("df_cast_1980.pkl")
df_cast_1990 = pd.read_pickle("df_cast_1990.pkl")
df_cast_1995 = pd.read_pickle("df_cast_1995.pkl")
df_cast_2000 = pd.read_pickle("df_cast_2000.pkl")
df_cast_2005 = pd.read_pickle("df_cast_2005.pkl")
df_cast_2010 = pd.read_pickle("df_cast_2010.pkl")
df_cast_2015 = pd.read_pickle("df_cast_2015.pkl")
df_cast_2023 = pd.read_pickle("df_cast_2023.pkl")
df_cast = pd.concat([df_cast_1960, df_cast_1970, df_cast_1980, df_cast_1990, df_cast_1995, df_cast_2000, df_cast_2005, df_cast_2010, df_cast_2015, df_cast_2023])

df_genres_1960 = pd.read_pickle("df_genres_1960.pkl")
df_genres_1980 = pd.read_pickle("df_genres_1980.pkl")
df_genres_2000 = pd.read_pickle("df_genres_2000.pkl")
df_genres_2010 = pd.read_pickle("df_genres_2010.pkl")
df_genres_2023 = pd.read_pickle("df_genres_2023.pkl")
df_genres = pd.concat([df_genres_1960, df_genres_1980, df_genres_2000, df_genres_2010, df_genres_2023])

df_movies = df_cast.merge(df_genres, on=['q.value', 'd.value'], how='left')

df_movies = df_movies.groupby(['q.value', 'qLabel.value', 'IMDb_ID.value'], as_index=False).aggregate({'d.value':'min', 'duration.value':'first', 'genres.value':'first', 'cast.value': 'first', 'directors.value':'first'}) # Some films got more than one line due to API bug - not only first release date, but more or two durations different by one minute

# Remove from db movies with duplicated names (two different films with the same name would be ambiguous - moreover there are only less than 30 movies like that)
dups = df_movies[df_movies.duplicated('q.value', keep=False) == True]['qLabel.value'].unique()
df_movies = df_movies[~df_movies['qLabel.value'].isin(dups)]

# Ensure dtypes
df_movies[['d.value', 'duration.value']] = df_movies[['d.value', 'duration.value']].apply(pd.to_numeric)
df_movies[['q.value', 'qLabel.value', 'IMDb_ID.value', 'genres.value', 'cast.value', 'directors.value']] = df_movies[['q.value', 'qLabel.value', 'IMDb_ID.value', 'genres.value', 'cast.value', 'directors.value']].astype(str)

# Sort the comma delimited values inside the columns cast and genres
def sort_values_inside_col(str_input):
    delim = ", "
    str_input_new = delim.join(sorted(str_input.split(', ')))
    return str_input_new
df_movies['cast.value'] = df_movies['cast.value'].apply(sort_values_inside_col)
df_movies['genres.value'] = df_movies['genres.value'].apply(sort_values_inside_col)

# Re-sort by date
df_movies = df_movies.sort_values('d.value')

# Save to pickle for later use
df_movies.to_pickle("df_movies.pkl")