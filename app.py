import streamlit as st
import pandas as pd
import joblib
import requests


# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)


# =========================================
# LOAD MODEL FILES
# =========================================

movies = joblib.load("movies.pkl")
similarity = joblib.load("similarity.pkl")


# =========================================
# TMDB API KEY
# =========================================

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]


# =========================================
# GET MOVIE DETAILS FROM TMDB
# =========================================

def get_movie_details(movie_title):

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

    except requests.exceptions.RequestException:

        return None

    data = response.json()

    results = data.get("results", [])

    if len(results) == 0:

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

def recommend(movie):

    movie_index = movies[
        movies["title"] == movie
    ].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []

    for i in movie_list:

        recommendations.append(
            movies.iloc[i[0]]["title"]
        )

    return recommendations


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

movie_list = movies["title"].dropna().sort_values().values

selected_movie = st.selectbox(
    "🔎 Select a movie",
    movie_list
)


# =========================================
# RECOMMEND BUTTON
# =========================================

if st.button("🎯 Recommend Movies"):

    recommendations = recommend(selected_movie)

    st.subheader(
        f"Movies similar to {selected_movie}"
    )

    columns = st.columns(5)

    for column, movie in zip(
        columns,
        recommendations
    ):

        with column:

            details = get_movie_details(movie)

            # ---------------------------------
            # TMDB DETAILS AVAILABLE
            # ---------------------------------

            if details is not None:

                poster = details["poster"]

                # Movie poster
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

                    st.write("🎬 No poster available")

                # Movie title
                st.markdown(
                    f"### {movie}"
                )

                # Rating
                rating = details["rating"]

                if rating:

                    st.write(
                        f"⭐ {rating:.1f}/10"
                    )

                # Release year
                release_date = details["release_date"]

                if release_date:

                    st.write(
                        f"📅 {release_date[:4]}"
                    )

                # Overview
                overview = details["overview"]

                if overview:

                    if len(overview) > 180:

                        overview = overview[:180] + "..."

                    st.write(overview)

            # ---------------------------------
            # TMDB NOT AVAILABLE
            # ---------------------------------

            else:

                st.markdown(
                    f"### {movie}"
                )

                st.warning(
                    "Movie information unavailable."
                )


# =========================================
# FOOTER
# =========================================

st.divider()

st.caption(
    "Movie data and images provided by TMDB."
)