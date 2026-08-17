def recommend(movie):

    movie_indices = movies[
        movies["title"] == movie
    ].index

    if len(movie_indices) == 0:
        return []

    index = movie_indices[0]

    distances = list(
        enumerate(similarity[index])
    )

    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for item in distances[1:6]:

        movie_index = item[0]

        movie_data = movies.iloc[movie_index]

        similarity_score = item[1] * 100

        recommendations.append({
            "title": movie_data["title"],
            "similarity": similarity_score,
            "overview": movie_data.get(
                "overview",
                "No overview available."
            ),
            "genres": movie_data.get(
                "genres",
                []
            ),
            "release_date": movie_data.get(
                "release_date",
                "Unknown"
            ),
            "rating": movie_data.get(
                "vote_average",
                0
            ),
            "votes": movie_data.get(
                "vote_count",
                0
            ),
            "director": movie_data.get(
                "crew",
                "Unknown"
            )
        })

    return recommendations