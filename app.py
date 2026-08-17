import streamlit as st
import pandas as pd
import joblib
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)


# =========================================
# LOAD MOVIES
# =========================================

@st.cache_data
def load_movies():

    movies = joblib.load("movies.pkl")

    movies["tags"] = (
        movies["tags"]
        .fillna("")
        .astype(str)
    )

    return movies


movies = load_movies()


# =========================================
# CREATE TF-IDF MODEL
# =========================================

@st.cache_resource
def create_recommendation_model(movies):

    vectorizer = TfidfVectorizer(
        max_features=10000,
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(
        movies["tags"]
    )

    model = NearestNeighbors(
        n_neighbors=6,
        metric="cosine",
        algorithm="brute"
    )

    model.fit(vectors)

    return vectorizer, model, vectors


vectorizer, model, vectors = create_recommendation_model(
    movies
)


# =========================================
# TMDB API KEY
# =========================================

try:

    TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

except Exception:

    TMDB_API_KEY = ""


# =========================================
# GET MOVIE DETAILS FROM TMDB
# =========================================

@st.cache_data(ttl=3600)
def get_movie_details(movie_title):

    if not TMDB_API_KEY:

        return None

    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_title
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.RequestException:

        return None

    results = data.get("results", [])

    if not results:

        return None

    movie = results[0]

    return {
        "poster": movie.get("poster_path"),
        "rating": movie.get("vote_average", 0),
        "overview": movie.get("overview", ""),
        "release_date": movie.get("release_date", "")
    }


# =========================================
# RECOMMENDATION FUNCTION
# =========================================

def recommend(movie_title):

    movie_indices = movies.index[
        movies["title"] == movie_title
    ].tolist()

    if not movie_indices:

        return []

    movie_index = movie_indices[0]

    movie_vector = vectors[movie_index]

    distances, indices = model.kneighbors(
        movie_vector,
        n_neighbors=6
    )

    recommendations = []

    for index in indices[0]:

        if index == movie_index:

            continue

        recommendations.append(
            movies.iloc[index]["title"]
        )

    return recommendations[:5]


# =========================================
# HEADER
# =========================================

st.title("🎬 Movie Recommendation System")

st.write(
    "Discover movies similar to your favorite movie."
)


# =========================================
# MOVIE SELECTION
# =========================================

movie_list = (
    movies["title"]
    .dropna()
    .sort_values()
    .values
)

selected_movie = st.selectbox(
    "🔎 Select a movie",
    movie_list
)


# =========================================
# RECOMMEND BUTTON
# =========================================

if st.button(
    "🍿 Recommend Movies",
    key="recommend_button"
):

    recommendations = recommend(
        selected_movie
    )

    st.subheader(
        f"🎬 Movies similar to {selected_movie}"
    )

    if not recommendations:

        st.warning(
            "No recommendations found."
        )

    else:

        columns = st.columns(5)

        for column, movie in zip(
            columns,
            recommendations
        ):

            with column:

                details = get_movie_details(
                    movie
                )

                # ---------------------------------
                # TMDB DETAILS AVAILABLE
                # ---------------------------------

                if details is not None:

                    poster = details["poster"]

                    if poster:

                        poster_url = (
                            "https://image.tmdb.org/t/p/w500"
                            + poster
                        )

                        st.image(
                            poster_url,
                            use_container_width=True
                        )

                    else:

                        st.write(
                            "🎬 No poster available"
                        )

                    st.markdown(
                        f"### {movie}"
                    )

                    rating = details["rating"]

                    if rating:

                        st.write(
                            f"⭐ Rating: {rating:.1f}/10"
                        )

                    release_date = (
                        details["release_date"]
                    )

                    if release_date:

                        st.write(
                            f"📅 {release_date}"
                        )

                    overview = details["overview"]

                    if overview:

                        st.write(
                            overview
                        )

                # ---------------------------------
                # TMDB NOT AVAILABLE
                # ---------------------------------

                else:

                    st.markdown(
                        f"### 🎬 {movie}"
                    )

                    st.info(
                        "Movie details are currently unavailable."
                    )