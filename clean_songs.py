# %%
import polars as pl
# %%
df = pl.read_csv("data/artist_songs.csv")
# %%
df = df.filter(pl.col("primary_artist") == "Caparezza")
# %%
df = df.filter(
    ~pl.col("title").str.to_lowercase().str.contains("remix|live|demo|radio|skit")
)
# %%
df.write_csv("data/caparezza_songs.csv")
# %%
