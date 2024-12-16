import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=72ee23ef1fc80397f16f7c96a7c59e87&language=en-US')
    data = response.json()
    if 'poster_path' in data and data['poster_path']:
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

def recommend(movie):
    # Get the index of the selected movie
    movie_index = movies[movies['title'] == movie].index[0]

    # Retrieve the similarity scores
    distances = similarity[movie_index]

    # Enumerate and sort distances, excluding the movie itself
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])
    movies_list = [m for m in movies_list if m[0] != movie_index][:5]

    # Generate a list of recommended movie titles
    recommended_movies = []
    recommended_movies_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        # fetch poster from API
        recommended_movies_poster.append(fetch_poster(movie_id))
    return recommended_movies,recommended_movies_poster

movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title("Movie Recommender System")

selected_movies_name = st.selectbox(
    'Which movie do you want to watch',
    movies['title'].values
)

# if st.button('Recommend'):
#     recommendations = recommend(selected_movies_name)
#     for i in recommendations:
#         st.write(selected_movies_name)

# if st.button('Recommend'):
#     names,poster = recommend(selected_movies_name)
#     # st.subheader(f"Movies similar to {selected_movies_name}:")
#     # for i, rec in enumerate(recommendations, start=1):
#     #     st.write(f"{i}. {rec}")
#     col1,col2,col3,col4,col5 = st.columns(5)
#     with col1:
#         st.header(names[0])
#         st.image(poster[0])

#     with col2:
#         st.header(names[1])
#         st.image(poster[1])

#     with col3:
#         st.header(names[2])
#         st.image(poster[2])

#     with col4:
#         st.header(names[3])
#         st.image(poster[3])

#     with col5:
#         st.header(names[4])
#         st.image(poster[4])

if st.button('Recommend'):
    names, posters = recommend(selected_movies_name)
    
    # Create a row with columns
    cols = st.columns(5)  # Creates 5 equal-width columns

    # Populate each column with a movie title as header and its poster
    for col, name, poster in zip(cols, names, posters):
        with col:
            # Use markdown to set the font size for the movie name
            st.markdown(f"<h5 style='text-align: center;'>{name}</h5>", unsafe_allow_html=True)  # Smaller header
            st.image(poster, use_container_width=True)  # Movie poster