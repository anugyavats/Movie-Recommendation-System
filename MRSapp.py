import streamlit as st
import pickle
import pandas as pd
import requests
import textwrap


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


movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Google Drive link to the similarity1.pkl file
similarity_link = "https://drive.google.com/file/d/1MuBCHO6kjqfa0jW1UVWHMjB9f4oasWq6/view?usp=sharing"

# Extract the file ID from the Google Drive link
file_id = similarity_link.split("/")[5]

# Construct the download link using the file ID
download_link = f"https://drive.google.com/uc?export=download&id={file_id}"

# Download the similarity1.pkl file using requests
response = requests.get(download_link)
content = response.content

# Save the downloaded content to a file
with open('similarity1_downloaded.pkl', 'wb') as f:
    f.write(content)

# Load the saved file and verify its content
try:
    with open('similarity1_downloaded.pkl', 'rb') as f:
        similarity = pickle.load(f)
    print("The downloaded file has the correct content.")
except pickle.UnpicklingError as e:
    print("Error: Failed to load the downloaded file.")
    print(e)


def recommend(movie, similarity):
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


st.title('Movie Recommendation System')

selected_movie_name = st.selectbox(
    'Search a Movie',
    movies['title'].values)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_overviews = recommend(selected_movie_name, similarity)
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
