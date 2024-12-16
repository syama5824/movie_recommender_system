import numpy as np
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

movies = movies.merge(credits,on='title') # merging two dataframes

movies.isnull().sum()
#there are 3 rows in overview category which are not known
#we shall drop those rows as 3 is not a big number
movies.dropna(inplace=True)

#searching if any dupliactes present
movies.duplicated().sum()

#string of list of dictionaries -> List of dictionaries -> list
#we can create a helper function
def converter(obj):
    List = []
    for i in ast.literal_eval(obj):
        List.append(i['name'])
    return List

movies['genres'] = movies['genres'].apply(converter)
movies['keywords'] = movies['keywords'].apply(converter)

# i'm taking first 5 actors of each movie and extracting name from all
def converter5(obj):
    List = []
    counter=0
    for i in ast.literal_eval(obj):
        if counter!=5:
            List.append(i['name'])
            counter+=1
        else:
            break
            
    return List
    
movies['cast'] = movies['cast'].apply(converter5)

def fetch_director(obj):
    List = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            List.append(i['name'])
            break
            
    return List

movies['crew'] = movies['crew'].apply(fetch_director)

#overview is a string. Let's convert it into list so that we can concatenate with other columns
movies['overview'] = movies['overview'].apply(lambda x:x.split())
#removing spaces in overview,genres,keywords,cast and crew
movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ","") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ","") for i in x])
movies['cast'] = movies['cast'].apply(lambda x:[i.replace(" ","") for i in x])
movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ","") for i in x])

movies['tags'] = movies['overview']+movies['genres']+movies['keywords']+movies['cast']+movies['crew']
movies_new = movies[['movie_id','title','tags']]
movies_new.loc[:,'tags'] = movies_new['tags'].apply(lambda x: " ".join(x) if isinstance(x, list) else x)
movies_new.loc[:,'tags'] = movies_new['tags'].apply(lambda x:x.lower())

# Text Vectorization

ps = PorterStemmer()
# we are steeming as we want to convert all tenses into simple present

def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))

    return " ".join(y)

movies_new.loc[:,'tags'] = movies_new['tags'].apply(stem)
# calculating similarity score between two tags to know if they are similar, and should be recommended
# remove stopwords
cv = CountVectorizer(max_features=5000,stop_words='english')
# convert movies into vectors
vectors = cv.fit_transform(movies_new['tags']).toarray()
cv.get_feature_names_out()
movies_new.shape
similarity = cosine_similarity(vectors)
# Assuming the recommend function is defined and similairty matrix is pre-computed
def recommend(movie):
    # Find the index of the movie in the DataFrame
    movie_index = movies_new[movies_new['title'] == movie].index[0]
    
    # Assuming similairty is a pre-computed matrix of distances or similarities
    distances = similarity[movie_index]
    
    # Get the top 5 similar movies (excluding the input movie itself)
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    # Get the movie titles for the top 5 recommendations
    # recommended_movies = [movies_new.iloc[i[0]]['title'] for i in movies_list]
    
    # return recommended_movies
    for i in movies_list:
        print(movies_new.iloc[i[0]].title)

recommend('Avatar')