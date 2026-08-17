import pandas as pd

movies = pd.read_csv("dataset/tmdb_5000_movies.csv")
credits = pd.read_csv("dataset/tmdb_5000_credits.csv")

print("Movies Dataset")
print("----------------")
print("Shape:", movies.shape)
print(movies.head())

print("\nCredits Dataset")
print("----------------")
print("Shape:", credits.shape)
print(credits.head())