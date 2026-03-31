# db.py - Database configuration for Tokyo OSM data / 東京OSMデータのデータベース設定
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -------------------------
# DATABASE CONFIG / データベース設定
# -------------------------
# Docker Postgres with Kanto OSM data / 関東OSMデータを使ったDocker上のPostgres
DATABASE_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm"

# Force UTF-8 encoding / UTF-8エンコーディングを強制
engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "UTF8"},  # クライアントエンコーディング指定
    # encoding='CP932'  # 旧Shift-JISの場合（コメントアウト中）
    pool_pre_ping=True,  # コネクションの有効性を事前確認
    future=True  # SQLAlchemy 2.0 互換モード
)

# Optional: create session / セッション生成（オプション）
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,     # 自動フラッシュ無効
    autocommit=False     # 自動コミット無効
)