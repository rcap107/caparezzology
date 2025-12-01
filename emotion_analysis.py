# %%
from transformers import pipeline
import polars as pl

classifier = pipeline(
    "text-classification", model="MilaNLProc/feel-it-italian-emotion", top_k=2
)
# %%
with open(
    'data/lyrics/album:"Prisoner 709"(2017)/_Larsen (Capitolo_ La Tortura)_.txt'
) as f:
    lyrics = f.readlines()
predictions = classifier(lyrics)
df = pl.DataFrame({"lyric": lyrics, "predictions": [str(pred) for pred in predictions]})
# %%
from pathlib import Path
from tqdm import tqdm

for album in tqdm(
    Path("data/lyrics").iterdir(), total=Path("data/lyrics").stat().st_nlink - 2
):
    if album.is_dir():
        if album.with_suffix(".parquet").exists():
            tqdm.write(f"Skipping {album.name}, parquet file already exists.")
            continue
        album_name = album.name.removeprefix('album:"')
        album_dfs = []
        for lyric_file in tqdm(
            sorted(list(album.iterdir())), desc=f"Processing album: {album_name}"
        ):
            if lyric_file.suffix == ".txt":
                song_name = lyric_file.stem
                tqdm.write(f"Processing {album_name} - {song_name}...")
                with open(lyric_file) as f:
                    lyrics = f.readlines()
                try:
                    predictions = classifier(lyrics)
                except RuntimeError as e:
                    tqdm.write(f"  Error processing {song_name}: {e}")
                    raise e
                df = pl.DataFrame(
                    {
                        "album": album_name,
                        "song": song_name,
                        "lyric": lyrics,
                        "predictions": predictions,
                    }
                )
                album_dfs.append(df)
        output_file = album.with_suffix(".parquet")
        album_df = pl.concat(album_dfs)
        album_df.write_parquet(output_file)
# %%
