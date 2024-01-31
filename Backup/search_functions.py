import pandas as pd

# Worfklow:
# 1. User puts name of the movie in english in the app

# To-do: get this input below from Flask app instead of hardcoded
user_input = str('Cleopatra')  # 'Cleopatra' 'The Curious Case of Benjamin Button' or 'The Curious Case of Benjamin'

df_movies = pd.read_pickle('../df_movies.pkl')
df_movies_search = df_movies[df_movies[
                                 'qLabel.value'] != user_input]  # The same data excluding the user input movie, used for searching for recommendation


# 2. The app filter the movies based on the input from user; only one row is returned
def get_info_from_input(u_input):
    df_input = df_movies[df_movies['qLabel.value'] == u_input]
    if len(df_input) == 0:
        print("I'm sorry, currently this movie is not in the database :( Please try with another movie.")
        exit()
    elif len(df_input) > 1:
        print("There are more than 1 movie with this name - using the oldest out of them.")
        df_input = df_input.nsmallest(n=1, columns="d.value")
    else:
        pass
    return (df_input)


movie_input = get_info_from_input(u_input=user_input)
print(movie_input)


# To-do: Print this in a table for the user to see what movie he is searching

# 3. Similar movie is returned based on few steps: step1 - movies with the same set of genres

def find_similar(df_input):
    delim = "|"

    movie_input_genres = df_input.iloc[0]['genres.value']
    list_genres = delim.join((movie_input_genres.split(', ')))

    movie_input_directors = df_input.iloc[0]['directors.value']
    list_directors = delim.join((movie_input_directors.split(', ')))

    movie_input_cast = df_input.iloc[0]['cast.value']
    list_cast = delim.join((movie_input_cast.split(', ')))

    similar_genres = df_movies_search[df_movies_search['genres.value'] == movie_input_genres]
    # if there is a match on genres right away use first movie, if multiple matches pick the oldest
    if len(similar_genres) == 1:
        similar_movie = similar_genres
    elif len(similar_genres) > 1:
        similar_movie = similar_genres.nsmallest(n=1, columns="d.value")
    else:  # if there is no perfect match on genres get movies with at least one same genre and filter further

        step1_df = df_movies_search[
            df_movies_search['genres.value'].str.contains(list_genres)]  # at least one genre is the same
        print(f"Length of step1_df (at least one genre matching) is: {len(step1_df)}")
        if len(step1_df) == 0:  # NoMatch
            print("I'm sorry, I could not find any similar movie :( Please try with another movie.")
            return
        elif len(step1_df) == 1:
            similar_movie = step1_df
        elif len(step1_df) <= 10:
            similar_movie = step1_df.nsmallest(n=1, columns="d.value")
        else:  # if there are still many films try with director

            step2_df = step1_df[
                step1_df['directors.value'].str.contains(list_directors)]  # at least one director is the same
            print(
                f"Length of step2_df (number of movies with at least one genre and at least one director matching) is: {len(step2_df)}")
            if len(step2_df) == 1:
                similar_movie = step2_df
            elif 0 < len(step2_df) <= 10:
                similar_movie = step2_df.nsmallest(n=1, columns="d.value")
            else:  # a lot of films - try with cast

                if len(step2_df) != 0:
                    step3_df = step2_df[
                        step2_df['cast.value'].str.contains(list_cast)]  # at least one cast member is the same
                    print(
                        f"Length of step3_df (number of movies with at least one genre, at least one director matching and at least one cast member matching) is: {len(step3_df)}")
                    similar_movie = step3_df.nsmallest(n=1, columns="d.value")
                else:  # NoMatch - if not directors then maybe cast?
                    step3_df = step1_df[
                        step1_df['cast.value'].str.contains(list_cast)]  # at least one director is the same
                    print(
                        f"Length of step3_df (number of movies with at least one genre, NONE director matching and at least one cast member matching) is: {len(step3_df)}")
                    if len(step3_df) == 0:
                        similar_movie = step1_df.nsmallest(n=1,
                                                           columns="d.value")  # pick from the first step, because there is no movie with any of the cast members or directors similar - only the genre
                    if len(step3_df) == 1:
                        similar_movie = step3_df
                    else:
                        similar_movie = step3_df.nsmallest(n=1,
                                                           columns="d.value")  # if still many matches pick from this step
    return (similar_movie)


similar = find_similar(df_input=movie_input)
print(similar)