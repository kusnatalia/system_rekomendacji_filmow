#this part gets the list of films from wikipedia and list of actors that play in them
import requests
import pandas as pd
import json
import lxml

url = 'https://query.wikidata.org/sparql'
query_working = '''
SELECT ?film ?filmLabel ?genere ?d WHERE {
  {
    SELECT ?film (GROUP_CONCAT(DISTINCT ?gL; SEPARATOR = ", ") AS ?genere) (MIN(YEAR(?date)) AS ?d) WHERE {
      ?sitelink schema:about ?director;
        schema:isPartOf <https://en.wikipedia.org/>;
        schema:name "Steven Spielberg"@en. # Edit this with different director's name to see their films. Use the English Wikipedia title only.
      ?film wdt:P31 wd:Q11424;
        wdt:P136 ?g, ?g.
      ?g rdfs:label ?gL.
      ?film wdt:P57 ?director;
        wdt:P577 ?date.
      FILTER((LANG(?gL)) = "en")
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    GROUP BY ?film
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC (?d)
'''
query_not_working = '''
SELECT ?film ?filmLabel ?genreLabel (MIN(?date) AS ?firstReleaseDate) ?directorLabel ?castMemberLabel ?duration
WHERE {
  ?film wdt:P31 wd:Q11424;  # Instance of film
        wdt:P577 ?date;    # Release date
        wdt:P57 ?director;  # Director
        wdt:P161 ?castMember;  # Cast member
        wdt:P2047 ?duration;  # Duration
        wdt:P136 ?genre.   # Genre

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?film ?filmLabel ?genreLabel ?directorLabel ?castMemberLabel ?duration
ORDER BY ?firstReleaseDate
'''

query_notsure = '''
SELECT ?film ?filmLabel ?date
WHERE {
  ?film wdt:P31 wd:Q11424;  # Instance of film
        wdt:P577 ?date.     # Release date

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?date
LIMIT 10
'''


# PREFIX wd: <http://www.wikidata.org/entity/> 
# PREFIX wdt: <http://www.wikidata.org/prop/direct/>
query = '''
SELECT ?q ?castMember ?castMemberLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  
  ?q wdt:P31 wd:Q11424;
  wdt:P364 wd:Q1860.
     wdt:P161 ?castMember.
}
'''


####Comments (commenting in query will not work, so the lines are copied here below):
### Examples of main query
#SELECT ?item ?itemLabel ?linkcount WHERE {
#     ?item wdt:P31/wdt:P279* wd:Q35666 .
#     ?item wikibase:sitelinks ?linkcount .
# FILTER (?linkcount >= 1) .
# SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . }
# }

  ## Filter for films with English labels
  #FILTER(LANG(?filmLabel) = "en" && LANG(?genreLabel) = "en" && LANG(?directorLabel) = "en" && LANG(?castMemberLabel) = "en")

#      ?sitelink schema:about ?director;
        # schema:isPartOf <https://en.wikipedia.org/>;
        # schema:name "Steven Spielberg"@en. # Edit this with different director's name to see their films. Use the English Wikipedia title only.
### At the very bottom of query:
#GROUP BY ?item ?itemLabel ?linkcount
#ORDER BY DESC(?linkcount)

#r = requests.get(url, params = {'format': 'json', 'query': query})
# print(r)
# data = r.json()
# print(data)

# data = requests.get(url, params = {'format': 'json', 'query': query}).text
# print(data)
# #data = ''.join((i for i in data if 0x20 <= ord(i) < 127))  # filter out unwanted chars
# json_data = json.loads(data, strict=False)

data = requests.get(url, params = {'format': 'json', 'query': query}).text

with open("Output.json", "w+", encoding = "UTF-8") as f:
    f.write(data)

#print(data)
data = open("Output.json")
df = pd.read_json(data)
print(df.head(5))

# df = pd.json_normalize(data['results']['bindings'], max_level=1)
#df = df[df.columns[df.columns.str.endswith('.value')]]

# print(df.head(5))
#print(df.columns[df.columns.str.endswith('.value')])















###SOME WORKING EXAMPLES

##working film label, IMDb_ID, date published, duration
# SELECT ?q ?qLabel ?IMDb_ID ?date ?duration ?genre ?genreLabel ?director  WHERE {
#   # Language filter for English labels
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
#   
#   ?q wdt:P31 wd:Q11424; #/wdt:P279*
#      wdt:P345 ?IMDb_ID; #IMDb ID
#      wdt:P577 ?date;     # Release date
#      wdt:P2047 ?duration;  # Duration
#      wdt:P136 ?genre;   # Genre
#      wdt:P57 ?director.  # Director
# #   ?genre rdfs:label ?genreLabel.
# #      wdt:P161 ?castMember.  # Cast member


## working genres with labels
#   SELECT ?q ?genre ?genreLabel WHERE {
#   # Language filter for English labels
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
#   
#   ?q wdt:P31 wd:Q11424; #/wdt:P279*
#      wdt:P136 ?genre;   # Genre
     
     
#   SELECT ?qLabel (MIN(YEAR(?date)) AS ?dateyear) (GROUP_CONCAT(DISTINCT ?castMember; SEPARATOR = ", ") AS ?castMemberL) WHERE {
#   # Language filter for English labels
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  
#   ?q wdt:P31 wd:Q11424; #/wdt:P279*
#      wdt:P577 ?date.
#   FILTER(YEAR(?date) = 2023)# Release date
    
#   OPTIONAL { ?q wdt:P161 ?castMember} # CastMember

# }
# GROUP BY ?qLabel
# ORDER BY DESC (?date)