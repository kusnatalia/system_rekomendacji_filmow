#The below script has been run multiple times adjusting manually start and end date to avoid reaching timout error on SPARQL query

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

### getting the cast info
sparql.setQuery("""
SELECT ?q ?qLabel ?duration ?cast ?d WHERE {
  {
    SELECT ?q ?qLabel ?duration (GROUP_CONCAT(DISTINCT ?castMemberL; SEPARATOR = ", ") AS ?cast) (MIN(YEAR(?date)) AS ?d) WHERE {
    ?q wdt:P31/wdt:P279* wd:Q11424;
        wdt:P495 wd:Q30; #country of origin US 
        wdt:P364 wd:Q1860; #original language polish: wd:Q809; or english: wd:Q1860
        wdt:P577 ?date;
        wdt:P2047 ?duration;  # Duration
        wdt:P161 ?castMember.
        ?castMember rdfs:label ?castMemberL.
    FILTER("2015-00-00"^^xsd:dateTime < ?date &&
         ?date <= "2023-00-00"^^xsd:dateTime)
    FILTER((LANG(?castMemberL)) = "en") #or en
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } #or en
  }
  GROUP BY ?q ?qLabel ?duration
  ORDER BY ?d
  }
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
results_df_cast = pd.json_normalize(results['results']['bindings'])
df_cast_2023 = results_df_cast[['q.value', 'qLabel.value', 'cast.value', 'd.value']]
df_cast_2023.to_pickle("df_cast_2023.pkl")