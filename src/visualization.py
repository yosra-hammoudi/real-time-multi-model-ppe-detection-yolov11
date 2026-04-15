import pandas as pd
import altair as alt

def create_realtime_chart(df, cam_id):
    if df is None or df.empty:
        return None

    if "camera_id" not in df.columns:
        return None

    df_cam = df[df["camera_id"] == cam_id]

    if df_cam.empty:
        return None

    chart = alt.Chart(df_cam).mark_line().encode(
        x="timestamp:T",
        y="nb_persons:Q"
    )

    return chart