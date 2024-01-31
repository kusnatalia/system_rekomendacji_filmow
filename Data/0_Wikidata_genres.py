#The below script has been run multiple times adjusting manually start and end date to avoid reaching timout error on SPARQL query

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

### getting the genres info
sparql.setQuery("""
SELECT ?q ?duration ?IMDb_ID ?directors ?genres ?d WHERE {
  {
    SELECT ?q ?duration ?IMDb_ID (GROUP_CONCAT(DISTINCT ?directorL; SEPARATOR = ", ") AS ?directors) (GROUP_CONCAT(DISTINCT ?genreL; SEPARATOR = ", ") AS ?genres) (MIN(YEAR(?date)) AS ?d) WHERE {
    ?q wdt:P31/wdt:P279* wd:Q11424;
        wdt:P495 wd:Q30; #country of origin US 
        wdt:P364 wd:Q1860; #original language polish: wd:Q809; or english: wd:Q1860
        wdt:P577 ?date;
        wdt:P2047 ?duration;  # Duration
        wdt:P345 ?IMDb_ID; # IMDb ID
        wdt:P57 ?director;  # Director
        wdt:P136 ?genre.
        ?genre rdfs:label ?genreL.
        ?director rdfs:label ?directorL.
    FILTER("2010-00-00"^^xsd:dateTime < ?date &&
         ?date <= "2023-00-00"^^xsd:dateTime)
    FILTER((LANG(?genreL)) = "en") #or en
    FILTER((LANG(?directorL)) = "en") #or en
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } #or en
  }
  GROUP BY ?q ?duration ?IMDb_ID
  ORDER BY ?d
  }
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
results_df_genres = pd.json_normalize(results['results']['bindings'])
df_genres_2023 = results_df_genres[['q.value', 'duration.value', 'IMDb_ID.value', 'genres.value', 'directors.value', 'd.value']]
df_genres_2023.to_pickle("df_genres_2023.pkl")