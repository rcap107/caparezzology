
# %%
import matplotlib.pyplot as plt


def get_color_for_emotion(emotion):
    color_map = {
        "joy": "yellow",
        "sadness": "blue",
        "anger": "red",
        "fear": "purple",
    }
    return color_map.get(emotion, "gray")

def plot_lyrics(lyrics, predictions):
    fig, ax = plt.subplots(figsize=(8, 16))
    fig.set_facecolor("#404040")

    emotions = [pred[0]["label"] if pred else "Unknown" for pred in predictions]
    confidences = [pred[0]["score"] if pred else 0 for pred in predictions]
    y_positions = range(len(lyrics))

    ax.set_ylim(-1, len(lyrics))
    for y, (lyric, emotion) in enumerate(zip(lyrics, emotions)):
        ax.text(
            0.5,
            y+0.5,
            lyric.strip(),
            ha="center",
            va="center",
            fontsize=10,
            fontdict={
                "family": "monospace",
                "weight": "bold",
            },
            # bbox=dict(
            #     boxstyle="round,pad=0.3",
            #     facecolor=get_color_for_emotion(emotion),
            #     alpha=0.1,
            # ),
            color=get_color_for_emotion(emotion),
            alpha=confidences[y],
        )
    ax.axis("off")
    plt.tight_layout()
    ax.invert_yaxis()

# %%
plot_lyrics(lyrics, predictions)