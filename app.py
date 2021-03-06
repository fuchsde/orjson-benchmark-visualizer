import streamlit as st
import requests, zipfile, io
from pathlib import Path
from functools import lru_cache
import pandas as pd
import plotly.express as px

# poetry run streamlit run app.py

@lru_cache(maxsize=4)
def download_content(url: str, dir: Path):
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(dir)

tmp_dir = Path("benchmarks/")

os_dict = {
"ubuntu": "https://storage.googleapis.com/orjson-benchmark/doc-ubuntu-18.04.zip",
"windows": "https://storage.googleapis.com/orjson-benchmark/doc-windows-latest.zip",
"mac": "https://storage.googleapis.com/orjson-benchmark/doc-macos-latest.zip"
}

st.set_page_config(layout="wide")
st.title("Orjson Benchmark Visualizer")

with st.sidebar:
    selected_os = st.selectbox("Choose OS", os_dict.keys())

    download_content(os_dict[selected_os], tmp_dir)

    benchmarks = list(filter(Path.is_dir, tmp_dir.glob("*/**")))
    benchmarks.remove(Path("benchmarks/latency"))
    benchmarks.remove(Path("benchmarks/types"))
    selected_benchmark = st.selectbox("Choose benchmark", benchmarks)

    results = list(filter(Path.is_file, Path(selected_benchmark).glob("*.json")))
    results.extend(list(filter(Path.is_file, Path(selected_benchmark).glob("*.rst"))))
    results = [result.name for result in results]
    selected_result = st.selectbox("Choose result", results)

if Path(selected_result).suffix == ".json":
    data_frame = pd.read_json(Path(selected_benchmark) / Path(selected_result), typ="series")
    data_frame = pd.json_normalize(data_frame.benchmarks)
    data_frame = data_frame.explode("stats.data")
    selected_group = st.selectbox("Choose group", data_frame["group"].unique())
    data_frame_filtered = data_frame[data_frame["group"] == selected_group]
    data_frame_filtered = data_frame_filtered.sort_values(by=["stats.data"])
    fig = px.box(data_frame_filtered, x="name", y="stats.data", color="params.library")
    st.plotly_chart(fig, use_container_width=True)

elif Path(selected_result).suffix == ".rst":
    with open(Path(selected_benchmark) / Path(selected_result), "r") as file:
        for line in file.readlines():
            st.text(line)

else:
    st.text("Unkown option")
