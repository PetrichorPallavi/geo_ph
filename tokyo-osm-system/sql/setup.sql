-- SQL setup script for Tokyo station and business search tables
-- 東京の駅と事業検索テーブルのSQLセットアップスクリプト
-- ==============================
-- 1. EXTENSIONS / 拡張機能
-- ==============================

-- Enable PostGIS for spatial data / 空間データ用PostGIS有効化
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable hstore for key-value tags / OSMタグ用hstore有効化
CREATE EXTENSION IF NOT EXISTS hstore;

-- ==============================
-- 2. INDEXES (CRITICAL) / インデックス（重要）
-- ==============================

-- For station filtering / 駅フィルター用
CREATE INDEX IF NOT EXISTS idx_planet_osm_point_railway
ON planet_osm_point (railway);

-- For spatial queries / 空間検索用
CREATE INDEX IF NOT EXISTS idx_planet_osm_point_way
ON planet_osm_point
USING GIST (way);

CREATE INDEX IF NOT EXISTS idx_planet_osm_polygon_way
ON planet_osm_polygon
USING GIST (way);

-- ==============================
-- 3. TOKYO STATIONS TABLE / 東京駅テーブル
-- ==============================

-- Drop old table if exists / 既存テーブル削除
DROP TABLE IF EXISTS tokyo_stations;

-- Create new stations table / 新規駅テーブル作成
CREATE TABLE tokyo_stations AS
SELECT
    name,                                -- Station name / 駅名
    ST_Y(ST_Transform(way, 4326)) AS lat, -- Latitude / 緯度
    ST_X(ST_Transform(way, 4326)) AS lon  -- Longitude / 経度
FROM planet_osm_point
WHERE railway = 'station'
AND name IS NOT NULL;

-- Index for fast lookup / 名前検索高速化
CREATE INDEX idx_tokyo_stations_name
ON tokyo_stations (name);

-- ==============================
-- 4. BUSINESS SEARCH TABLE / ビジネス検索テーブル
-- ==============================

-- Drop old table / 既存テーブル削除
DROP TABLE IF EXISTS tokyo_business_search;

-- Create business table from OSM points / OSMポイントからビジネステーブル作成
CREATE TABLE tokyo_business_search AS
SELECT
    osm_id,  -- 🔥 CRITICAL (for incremental updates / 増分更新用に必須)
    name,    -- Business name / 事業名
    amenity, -- Amenity type / 設備タイプ
    shop,    -- Shop type / 店舗タイプ
    COALESCE(tags->'addr:full', '') AS address,                  -- Full address / フルアドレス
    COALESCE(tags->'phone', tags->'contact:phone') AS phone,     -- Phone fallback / 電話番号
    tags->'website' AS website,                                  -- Website / ウェブサイト
    way                                                          -- Geometry / 幾何情報
FROM planet_osm_point
WHERE (
    amenity IS NOT NULL
    OR shop IS NOT NULL
)
AND name IS NOT NULL;

-- ==============================
-- 5. BUSINESS INDEXES / ビジネスインデックス
-- ==============================

-- 🔥 PRIMARY KEY (REQUIRED FOR UPSERT / UPSERT用必須)
ALTER TABLE tokyo_business_search
ADD CONSTRAINT pk_business_osm_id PRIMARY KEY (osm_id);

-- Spatial index / 空間検索用
CREATE INDEX idx_business_way
ON tokyo_business_search
USING GIST (way);

-- Text search indexes / テキスト検索用
CREATE INDEX idx_business_name
ON tokyo_business_search (name);

CREATE INDEX idx_business_amenity
ON tokyo_business_search (amenity);

CREATE INDEX idx_business_shop
ON tokyo_business_search (shop);

-- Optional: phone filter / 電話番号検索用（オプション）
CREATE INDEX idx_business_phone
ON tokyo_business_search (phone);

-- ==============================
-- 6. FULL TEXT SEARCH INDEX / フルテキスト検索インデックス
-- ==============================

-- Add tsvector column if missing / tsvector列追加
ALTER TABLE tokyo_business_search
ADD COLUMN IF NOT EXISTS search_text tsvector;

-- Populate search_text column / search_text列に値を設定
UPDATE tokyo_business_search
SET search_text =
    to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(amenity,'') || ' ' || coalesce(shop,''));

-- Create GIN index for full-text search / フルテキスト検索用GINインデックス
CREATE INDEX idx_business_search_text
ON tokyo_business_search
USING GIN (search_text);

-- ==============================
-- 7. DONE / 完了
-- ==============================

-- Verify counts / 件数確認
SELECT COUNT(*) FROM tokyo_stations;
SELECT COUNT(*) FROM tokyo_business_search;