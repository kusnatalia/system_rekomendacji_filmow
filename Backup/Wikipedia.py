#this part gets the plot/synopsis of the film from wikipedia
import wikipedia
import pandas as pd
import re

wikipedia.set_lang("en") #set language to english

def get_plot_text(movie_name, year):
    #movie_name - movie name in english, whitespaces allowed
    movie_name = str(movie_name)
    year = str(year)
    search = wikipedia.search(movie_name + " (" + year + " film)")
    page = wikipedia.page(search[0], auto_suggest=False).content
    try:
        page_plot = page.split("== Plot ==",1)[1]
        page_plot = page_plot.split("==",1)[0] #page_plot = re.split("\n", "", page_plot)[0]
        page_plot = re.sub('\n', ' ', page_plot)
    except:
        try: 
            page_plot = page.split("== Synopsis ==",1)[1]
            page_plot = page_plot.split("==",1)[0]
            page_plot = re.sub('\n', ' ', page_plot)
        except:
            try:
                page_plot = page.split("==",1)[0] #if no plot or synopsis print summary
            except:
                page_plot = ''
    return(page_plot)

test = get_plot_text(movie_name="A Midsummer Night's Dream", year=1968)
print(test)