import streamlit as st
import requests
import pandas as pd
# remove for company use
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

language = st.radio(
    "Language / 言語",
    ["日本語", "English"],
    horizontal=True
)

TEXT = {
    "日本語": {
        "title": "🚉 東京ビジネス検索",
        "subtitle": "エリアを選択して、周辺のレストランやオフィスを見つけましょう！",
        "area_select": "エリア選択",
        "radius": "半径（メーター）",
        "category": "カテゴリーを選択してください",
        "keyword": "キーワード検索（任意）",
        "limit": "表示件数",
        "search_button": "🔍 検索",
        "fetching": "近くのビジネスを取得しています...",
        "finding_station": "駅の位置を検索中...",
        "no_results": "該当する結果が見つかりませんでした。",
        "results_found": "件の結果が見つかりました。",
        "map_view": "📍 地図表示",
        "download": "📥 CSVダウンロード",
        "restaurant": "レストラン",
        "office": "オフィス"
    },
    "English": {
        "title": "🚉 Tokyo Business Finder",
        "subtitle": "Select an area to find nearby restaurants and offices.",
        "area_select": "Select Area",
        "radius": "Radius (meters)",
        "category": "Select Category",
        "keyword": "Keyword Search (Optional)",
        "limit": "Number of Results",
        "search_button": "🔍 Search",
        "fetching": "Fetching nearby businesses...",
        "finding_station": "Finding station location...",
        "no_results": "No matching results found.",
        "results_found": "results found.",
        "map_view": "📍 Map View",
        "download": "📥 Download CSV",
        "restaurant": "Restaurant",
        "office": "Office"
    }
}

t = TEXT[language]

st.set_page_config(page_title="Tokyo Business Finder", layout="wide")

st.title(t["title"])
st.markdown(t["subtitle"])

# -------------------------
# STATION LIST (Add More Later)
# -------------------------

stations_dict = {
    "秋葉原": "Akihabara",
    "東京": "Tokyo",
    "新宿": "Shinjuku",
    "渋谷": "Shibuya",
    "上野": "Ueno",
    "池袋": "Ikebukuro"
}

if language == "日本語":
    station_display = list(stations_dict.keys())
else:
    station_display = list(stations_dict.values())

selected_display = st.selectbox(t["area_select"], station_display)

if language == "English":
    reverse_lookup = {v: k for k, v in stations_dict.items()}
    selected_station = reverse_lookup[selected_display]
else:
    selected_station = selected_display

radius = st.slider(t["radius"], min_value=100, max_value=2000, value=300, step=100)

category = st.selectbox(
    t["category"],
    [t["restaurant"], t["office"]]
)

keyword = st.text_input(
    t["keyword"],
    placeholder="e.g. cafe, IT, ラーメン"
)

limit = st.slider("表示件数", min_value=10, max_value=100, value=10)

# -------------------------
# SEARCH BUTTON
# -------------------------

if st.button(t["search_button"]):

    overpass_url = "https://overpass-api.de/api/interpreter"

    # 1️⃣ Get Station Coordinates
    station_query = f"""
    [out:json];
    node["railway"="station"]["name"="{selected_station}"];
    out body;
    """

    with st.spinner(t["finding_station"]):

        try:
            station_response = requests.get(overpass_url, params={"data": station_query}, timeout=30, verify=False)
        except requests.exceptions.RequestException as e:
            st.error("Connection Error")
            st.text(str(e))
            st.stop()

    if station_response.status_code != 200:
        st.error("Failed to fetch station data.")
        st.stop()

    station_data = station_response.json()
    station_elements = station_data.get("elements", [])

    if not station_elements:
        st.error("Station not found.")
        st.stop()

    lat = station_elements[0]["lat"]
    lon = station_elements[0]["lon"]

    st.success(f"{selected_station} 周辺の検索を開始します。")

    # 2️⃣ Category Mapping
    if category == "レストラン":
        filter_tag = '["amenity"~"restaurant|cafe|fast_food|bar|pub|food_court"]'
    else:
        filter_tag = '["office"~"."]'

    # 3️⃣ Search Nearby Businesses
    business_query = f"""
    [out:json];
    node(around:{radius},{lat},{lon}){filter_tag};
    out body {limit};
    """

    with st.spinner(t["fetching"]):

        try:
            response = requests.get(
                overpass_url,
                params={"data": business_query},
                timeout=30,
                verify=False
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error("API Connection Error")
            st.text(str(e))
            st.stop()

    data = response.json()
    elements = data.get("elements", [])
    
    results = []

    for element in elements[:limit]:

        tags = element.get("tags", {})
        name = tags.get("name", "N/A")

        search_text = " ".join([
            name,
            tags.get("amenity", ""),
            tags.get("cuisine", "")
        ])

        if keyword and keyword.lower() not in search_text.lower():
            continue
        
        address_parts = [
            tags.get("addr:city", ""),
            tags.get("addr:street", ""),
            tags.get("addr:housenumber", "")
        ]

        address = ", ".join([p for p in address_parts if p])

        results.append({
            "Name": name,
            "Address": address if address else "N/A",
            "Latitude": element.get("lat"),
            "Longitude": element.get("lon"),
            "Category": category
        })

    df = pd.DataFrame(results)

    if df.empty:
        st.warning(t["no_results"])
        st.stop()

    st.success(f"{len(df)} {t['results_found']}")
    st.dataframe(df, width=True)

    # -------------------------
    # MAP VISUALIZATION
    # -------------------------

    st.subheader(t["map_view"])

    # Create map dataframe
    map_df = df.copy()

    # Add station row for visualization
    station_row = pd.DataFrame([{
        "Name": "Selected Station",
        "Address": "",
        "Latitude": lat,
        "Longitude": lon,
        "Category": "Station"
    }])

    map_df = pd.concat([station_row, map_df], ignore_index=True)

    st.map(
        map_df.rename(columns={
            "Latitude": "lat",
            "Longitude": "lon"
        })[["lat", "lon"]]
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label=t["download"],
        data=csv,
        file_name="tokyo_businesses.csv",
        mime="text/csv"
    )