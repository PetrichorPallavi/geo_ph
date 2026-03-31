# queries.py　- データベースクエリ定義
from sqlalchemy import create_engine, text

# -------------------------
# DATABASE ENGINE / データベース接続設定
# -------------------------
engine = create_engine(
    "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm",
    pool_pre_ping=True  # コネクションの事前確認
)

# -------------------------
# Stations / 駅情報取得
# -------------------------
def get_tokyo_stations():
    """
    Fetch Tokyo stations (name, lat, lon) / 東京の駅情報を取得（名前・緯度・経度）
    """
    sql = text("""
        SELECT name, lat, lon
        FROM tokyo_stations
        ORDER BY name
    """)
    with engine.connect() as conn:
        return conn.execute(sql).fetchall()

# -------------------------
# Business Search (Keyset Pagination) / ビジネス検索（Keyset Pagination）
# -------------------------
def search_places(search_term, lat, lon, radius, last_distance=None, last_name=None, limit=200):
    """
    Search businesses around a point with optional pagination
    / 指定地点周辺のビジネス検索（ページング対応）
    """

    # 👇 condition handled in Python (NO NULL issues)
    # Python側で条件処理（NULL問題回避）
    distance_filter = ""
    params = {
        "term": search_term,
        "like_term": f"%{search_term}%",
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "limit": limit
    }
    keyset_filter = ""

    # Keyset Pagination filter / Keyset Paginationフィルター
    if last_distance is not None and last_name is not None:
        keyset_filter = """WHERE (distance, name) > (:last_distance, :last_name)"""
        params["last_distance"] = float(last_distance)
        params["last_name"] = last_name

    sql = text(f"""
        WITH center AS (
            SELECT ST_Transform(
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                3857
            ) AS geom
        ),
        base AS (
            SELECT
                name,
                amenity,
                shop,
                address,
                phone,
                website,
                ST_Y(ST_Transform(way, 4326)) AS lat,
                ST_X(ST_Transform(way, 4326)) AS lon,
                ST_Distance(way, center.geom) AS distance
            FROM tokyo_business_search, center
            WHERE (
                search_text @@ plainto_tsquery('simple', :term)
                OR name ILIKE :like_term
            )
            AND ST_DWithin(way, center.geom, :radius)
            AND (phone IS NOT NULL AND phone != '')
        )
        SELECT *
        FROM base
        {keyset_filter}
        ORDER BY distance, name
        LIMIT :limit
    """)

    with engine.connect() as conn:
        return conn.execute(sql, params).fetchall()