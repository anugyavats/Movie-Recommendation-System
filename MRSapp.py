import streamlit as st
import pickle
import pandas as pd
import requests
import textwrap
import gdown

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def fetch_overview(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    overview = data['overview']
    return overview

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_overviews = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies_overviews.append(fetch_overview(movie_id))

    return recommended_movies, recommended_movies_posters, recommended_movies_overviews


movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

url = "https://drive.google.com/uc?export=download&id=1MuBCHO6kjqfa0jW1UVWHMjB9f4oasWq6"
response = requests.get(url)
with open("similarity1.pkl", "wb") as file:
    file.write(response.content)
    
# Load similarity1.pkl
with open("similarity1.pkl", "rb") as file:
    similarity = pickle.load(file)

st.title('Movie Recommendation System')

selected_movie_name = st.selectbox(
    'Search a Movie',
    movies['title'].values)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_overviews = recommend(selected_movie_name)
    num_movies = len(recommended_movie_names)
    num_columns = 5
    num_rows = (num_movies - 1) // num_columns + 1

    # Create the columns dynamically based on the number of recommended movies
    cols = [st.columns(num_columns) for _ in range(num_rows)]

    movie_index = 0
    for row in cols:
        for col in row:
            if movie_index < num_movies:
                with col:
                    # Wrap the title text to a maximum of 5 lines
                    title_lines = textwrap.wrap(recommended_movie_names[movie_index], width=20)
                    title_text = "\n".join(title_lines[:5])
                    st.text_area("Title", value=title_text, height=100)
                    st.image(recommended_movie_posters[movie_index])
                    # Display the complete overview
                    st.text_area("Overview", value=recommended_movie_overviews[movie_index], height=150)
                    movie_index += 1
