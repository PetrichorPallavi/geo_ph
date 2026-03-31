-- SQL script to create a business search table for Tokyo / 東京の事業検索テーブルを作成するSQLスクリプト

-- Drop existing table if exists / 既存テーブルがあれば削除
DROP TABLE IF EXISTS tokyo_business_search;

-- Create new table from planet_osm_point / planet_osm_point から新規テーブル作成
CREATE TABLE tokyo_business_search AS
SELECT
    name,                       -- Business name / 事業名
    amenity,                     -- Amenity type / 設備タイプ
    shop,                        -- Shop type / 店舗タイプ
    tourism,                     -- Tourism type / 観光施設タイプ
    tags->'phone' AS phone,      -- Phone number / 電話番号
    tags->'website' AS website,  -- Website URL / ウェブサイト
    tags->'addr:housenumber' AS housenumber,  -- House number / 番地
    tags->'addr:street' AS street,            -- Street name / 通り名
    way                          -- Geometry / 幾何情報
FROM planet_osm_point
WHERE name IS NOT NULL           -- Must have a name / 名前が必須
AND (
    amenity IS NOT NULL           -- Has amenity OR tourism type / 設備タイプまたは観光施設タイプがある
    OR tourism IS NOT NULL
);