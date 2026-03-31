# app/app.py　- Streamlitアプリケーション
import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from queries import search_places, get_tokyo_stations
import subprocess
from datetime import datetime
import os
import json
import time

st.set_page_config(layout="wide")
st.title("🗺️ 東京ビジネス検索デモ")  # Tokyo Business Search Demo

# -------------------------
# PATHS / パス
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TIME_FILE = os.path.join(BASE_DIR, "last_update.txt")  # 最終更新日時ファイル
STATUS_FILE = os.path.join(BASE_DIR, "status.json")   # ステータス保存ファイル
LOG_FILE = os.path.join(BASE_DIR, "update.log")       # ログファイル

# -------------------------
# STATUS HELPERS / ステータス補助関数
# -------------------------
def read_status():
    """Read current status from status.json / status.jsonからステータスを読む"""
    if not os.path.exists(STATUS_FILE):
        return {"status": "idle", "message": ""}

    try:
        with open(STATUS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {"status": "idle", "message": ""}
            return json.loads(content)
    except Exception:
        return {"status": "error", "message": "Invalid status file / 無効なステータスファイル"}

def write_status(status, message="", last_update=None):
    """Write status to status.json / status.jsonにステータスを書き込む"""
    data = {
        "status": status,
        "message": message,
        "last_update": last_update
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f)

# -------------------------
# STATIONS (cached) / 駅情報（キャッシュ）
# -------------------------
@st.cache_data
def load_stations():
    return get_tokyo_stations()

stations_data = load_stations()
stations = {row.name: (row.lat, row.lon) for row in stations_data}

# -------------------------
# SESSION STATE INIT / セッション初期化
# -------------------------
if "results" not in st.session_state:
    st.session_state.results = None

if "last_distance" not in st.session_state:
    st.session_state.last_distance = None

if "center" not in st.session_state:
    st.session_state.center = None

if "has_more" not in st.session_state:
    st.session_state.has_more = False

if "search_params" not in st.session_state:
    st.session_state.search_params = None

if "last_name" not in st.session_state:
    st.session_state.last_name = None

# -------------------------
# SIDEBAR - SEARCH SETTINGS / サイドバー検索設定
# -------------------------
st.sidebar.header("🔍 検索設定")

search_term = st.sidebar.text_input("検索キーワード", "カフェ")  # Search Keyword
radius = st.sidebar.slider("半径（メートル）", 100, 5000, 1000)  # Radius (meters)
station_name = st.sidebar.text_input("駅名", "秋葉原")          # Station Name

# -------------------------
# SEARCH BUTTON / 検索ボタン
# -------------------------
if st.sidebar.button("検索"):

    if station_name not in stations:
        st.error("駅が見つかりません")  # Station not found
        st.stop()
    
    lat, lon = stations[station_name]
    # RESET STATE / 状態リセット
    st.session_state.results = []
    st.session_state.last_distance = None
    st.session_state.has_more = True
    st.session_state.center = (lat, lon)

    # STORE PARAMS / パラメータ保存
    st.session_state.search_params = {
        "search_term": search_term,
        "radius": radius,
        "station_name": station_name
    }

    # FIRST LOAD / 初回検索
    results = search_places(
            search_term=search_term,
            lat=lat,
            lon=lon,
            radius=radius
        )

    if results:
        st.session_state.results.extend(results)
        st.session_state.last_distance = results[-1].distance
        st.session_state.last_name = results[-1].name
    else:
        st.session_state.has_more = False

results = st.session_state.results

# -------------------------
# UPDATE STATUS DISPLAY / ステータス表示
# -------------------------
st.sidebar.markdown("## 📊 更新ステータス")

status = read_status()

if status["status"] == "running":
    st.sidebar.warning("🟡 OSMを更新中...")
elif status["status"] == "processing":
    st.sidebar.info("🔵 データベースを更新中...")
elif status["status"] == "done":
    st.sidebar.success("🟢 完了")
    st.sidebar.write(status.get("last_update", ""))
elif status["status"] == "error":
    st.sidebar.error("🔴 更新失敗")
else:
    st.sidebar.write("⚪ 待機中")

st.sidebar.write(status.get("message", ""))

# -------------------------
# LOG VIEWER / ログ表示
# -------------------------
st.sidebar.markdown("## 📜 ログ")

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        logs = f.readlines()[-20:]
        st.sidebar.text("".join(logs))
else:
    st.sidebar.write("まだログはありません")

# -------------------------
# UPDATE BUTTON / データ更新ボタン
# -------------------------
st.sidebar.markdown("## 🔄 データ管理")

if os.path.exists(TIME_FILE):
    with open(TIME_FILE, "r") as f:
        last_update = f.read()
else:
    last_update = "未更新"

st.sidebar.write(f"最終更新日時: {last_update}")

if st.sidebar.button("データ更新"):

    write_status("running", "更新開始...")

    with open(LOG_FILE, "w") as log:
        process = subprocess.Popen(
            [
                "docker", "compose", "run", "--rm", "osm_updater"
            ],
            stdout=log,
            stderr=log,
            shell=False
        )

    st.sidebar.success("🚀 更新開始")

# -------------------------
# BACKGROUND MONITOR / バックグラウンド監視
# -------------------------
if status["status"] in ["running", "processing"]:

    # Check if docker process still running / Dockerプロセス確認
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True
        )

        if "osm_updater" not in result.stdout:
            # Step 2: refresh DB / DB更新
            write_status("processing", "DBを更新中...")

            subprocess.run(
                "Get-Content sql/incremental_update.sql | docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm",
                shell=True
            )

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            write_status("done", "更新完了", now)

            with open(TIME_FILE, "w") as f:
                f.write(now)

    except Exception as e:
        write_status("error", str(e))

    time.sleep(2)
    st.rerun()

# -------------------------
# RESULTS DISPLAY / 結果表示
# -------------------------
results = st.session_state.results

if results:

    df = pd.DataFrame(results)

    # Debug info (important) / デバッグ情報（重要）
    st.write(f"📊 読み込んだ件数: {len(df)-1}")

    # Ensure columns / 列確認
    for col in ["phone", "website"]:
        if col not in df.columns:
            df[col] = None

    df["phone_link"] = df["phone"].apply(
        lambda x: f"tel:{x}" if pd.notnull(x) and x else None
    )

    df = df.rename(columns={
        "name": "名前",
        "address": "住所",
        "distance": "距離(m)",
        "lat": "緯度",
        "lon": "経度",
        "phone_link": "電話",
        "website": "ウェブサイト"
    })

    # -------------------------
    # MAP / 地図
    # -------------------------
    st.subheader("地図")

    lat, lon = st.session_state.center

    m = folium.Map(location=[lat, lon], zoom_start=15)

    folium.Marker(
        [lat, lon],
        tooltip=st.session_state.search_params["station_name"],
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Limit markers for performance / パフォーマンスのため上限300件
    for _, r in df.head(300).iterrows():
        folium.Marker(
            [r["緯度"], r["経度"]],
            tooltip=r["名前"]
        ).add_to(m)

    st_folium(m, width=1200, height=500)

    # -------------------------
    # TABLE / テーブル
    # -------------------------
    st.subheader("検索結果")

    st.dataframe(
        df[["名前", "住所", "電話", "ウェブサイト", "距離(m)"]],
        width="stretch",
        height=600
    )
    # 👇 ADD THIS HERE
    if not st.session_state.has_more:
        st.info("これ以上データはありません")

# -------------------------
# LOAD MORE BUTTON / もっと見るボタン
# -------------------------
if st.session_state.results and st.session_state.has_more:

    if st.button("もっと見る"):

        params = st.session_state.search_params
        lat, lon = st.session_state.center

        more = search_places(
            params["search_term"],
            lat,
            lon,
            params["radius"],
            last_distance=st.session_state.last_distance,
            last_name=st.session_state.last_name
        )

        if more:
            st.session_state.results.extend(more)
            st.session_state.last_distance = more[-1].distance
            st.session_state.last_name = more[-1].name
        else:
            st.session_state.has_more = False

        st.rerun()


elif st.session_state.results == [] and st.session_state.search_params is not None:
    st.warning("終了しました。もっと見るデータはありません。")