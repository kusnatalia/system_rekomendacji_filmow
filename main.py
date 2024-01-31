from flask import Flask, render_template, request

import wikipedia
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By #needed for selecting the elements of the webpage
from fake_useragent import UserAgent


app= Flask (__name__)


@app.route("/")
def hello():
    return render_template('welcomepage.html')

@app.route('/movies')
def index():
    return render_template('movies.html')

@app.route('/movies_results', methods=['GET', 'POST'])
def search_movies():
    if request.method == 'GET':
        return f"The URL /movies_results is accessed directly. Try going to '/movies' to submit form"
    if request.method == 'POST':
        df_movies = pd.read_pickle('df_movies.pkl')
        query_df = get_info_from_input(df_movies, request.form['query'])

        query_wikidata = query_df.iloc[0]['q.value']
        query_name = query_df.iloc[0]['qLabel.value']
        query_duration = query_df.iloc[0]['duration.value']
        query_genres = query_df.iloc[0]['genres.value']
        query_cast = query_df.iloc[0]['cast.value']
        query_directors = query_df.iloc[0]['directors.value']
        query_date = query_df.iloc[0]['d.value']
        query_IMDB=query_df.iloc[0]['IMDb_ID.value']

        df_movies_search = df_movies[df_movies['qLabel.value'] != request.form['query']]  # The same data excluding the user input movie, used for searching for recommendation
        result_df = find_similar(df_movies_search, query_df)
        result_wikidata = result_df.iloc[0]['q.value']
        result_name = result_df.iloc[0]['qLabel.value']
        result_duration = result_df.iloc[0]['duration.value']
        result_genres = result_df.iloc[0]['genres.value']
        result_cast = result_df.iloc[0]['cast.value']
        result_directors = result_df.iloc[0]['directors.value']
        result_date = result_df.iloc[0]['d.value']
        result_IMDB = result_df.iloc[0]['IMDb_ID.value']

        query_opis_wikipedia = get_plot_text(query_name,query_date)
        result_opis_wikipedia = get_plot_text(result_name, result_date)
        query_rating=webscrap_rating(query_IMDB)
        result_rating=webscrap_rating(result_IMDB)
        jaccard_distance=DistJaccard(query_opis_wikipedia,result_opis_wikipedia)

        return render_template('movies_results.html',
                               query_wikidata=query_wikidata, query_name=query_name, query_duration=query_duration, query_genres=query_genres, query_cast=query_cast, query_directors=query_directors, query_date=query_date,
                               result_wikidata=result_wikidata, result_name=result_name, result_duration=result_duration, result_genres=result_genres, result_cast=result_cast, result_directors=result_directors, result_date=result_date,
                               query_opis_wikipedia=query_opis_wikipedia, result_opis_wikipedia=result_opis_wikipedia,
                               query_rating=query_rating, result_rating=result_rating,
                               jaccard_distance=jaccard_distance)

def DistJaccard(query_opis_wikipedia, result_opis_wikipedia):

    query_opis_wikipedia=re.sub('http\S+\s*','',query_opis_wikipedia)
    query_opis_wikipedia = re.sub('RT|cc', '', query_opis_wikipedia)
    query_opis_wikipedia = re.sub('#\S+', '', query_opis_wikipedia)
    query_opis_wikipedia=re.sub('[%s]'% re.escape("""!"#$%&'()"+,-./:;<=>?@[\]^_'{|}~"""),'',query_opis_wikipedia)
    query_opis_wikipedia=query_opis_wikipedia.lower()
    query_opis_wikipedia=query_opis_wikipedia.split(' ')
    query_opis_wikipedia = set(query_opis_wikipedia)

    result_opis_wikipedia=re.sub('http\S+\s*','',result_opis_wikipedia)
    result_opis_wikipedia = re.sub('RT|cc', '', result_opis_wikipedia)
    result_opis_wikipedia = re.sub('#\S+', '', result_opis_wikipedia)
    result_opis_wikipedia = re.sub('[%s]'% re.escape("""!"#$%&'()"+,-./:;<=>?@[\]^_'{|}~"""),'',result_opis_wikipedia)
    result_opis_wikipedia=result_opis_wikipedia.lower()
    result_opis_wikipedia=result_opis_wikipedia.split(' ')
    result_opis_wikipedia= set(result_opis_wikipedia)

    intersection = len(query_opis_wikipedia.intersection(result_opis_wikipedia))
    # Unions of two sets
    union = len(query_opis_wikipedia.union(result_opis_wikipedia))
    distance = intersection / union
    return distance.__round__(2)


def get_plot_text(movie_name, year):
    # movie_name - movie name in english, whitespaces allowed
    movie_name = str(movie_name)
    year = str(year)
    search = wikipedia.search(movie_name + " (" + year + " film)")
    page = wikipedia.page(search[0], auto_suggest=False).content
    try:
        page_plot = page.split("== Plot ==", 1)[1]
        page_plot = page_plot.split("==", 1)[0]  # page_plot = re.split("\n", "", page_plot)[0]
        page_plot = re.sub('\n', ' ', page_plot)
    except:
        try:
            page_plot = page.split("== Synopsis ==", 1)[1]
            page_plot = page_plot.split("==", 1)[0]
            page_plot = re.sub('\n', ' ', page_plot)
        except:
            try:
                page_plot = page.split("==", 1)[0]  # if no plot or synopsis print summary
            except:
                page_plot = ''
    return (page_plot)
def webscrap_rating(IMDb_ID):
    ua = UserAgent()
    userAgent = ua.random
    #print(userAgent)

    url = 'https://www.imdb.com/title/' + IMDb_ID +'/ratings/'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'user-agent={userAgent}')
    wd = webdriver.Chrome(options=chrome_options)

    try:
        wd.get(url)
    except:
        print("Some issue encountered while trying to read the webpage. Restarting the webdriver and trying again.")
        wd = webdriver.Chrome(options=chrome_options)
        wd.get(url)

    time.sleep(5) # Wait for webpage to load

    #wd.save_screenshot("screenshot.png")
    rating = wd.find_element(By.XPATH, ("//span[@class='sc-5931bdee-1 gVydpF']"))
    rating = rating.text

    wd.quit()
    return(rating)

def get_info_from_input(df_movies, u_input):
    df_input = df_movies[df_movies['qLabel.value'] == u_input]
    if len(df_input) == 0:
        print("I'm sorry, currently this movie is not in the database :( Please try with another movie.")
        exit()
    elif len(df_input) > 1:
        print("There are more than 1 movie with this name - using the oldest out of them.")
        df_input = df_input.nsmallest(n=1, columns="d.value")
    else:
        pass
    return df_input

def find_similar(df_movies_search, df_input):
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

if __name__ == '__main__':
    app.run(debug=True)

