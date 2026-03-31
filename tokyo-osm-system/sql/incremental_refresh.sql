-- Incremental refresh for tokyo_business_search table / tokyo_business_searchテーブルのインクリメンタルリフレッシュ

-- Insert or update businesses in tokyo_business_search
-- tokyo_business_search テーブルに新規追加または更新
INSERT INTO tokyo_business_search (
    osm_id,     -- OSM unique ID / OSM固有ID
    name,       -- Business name / 事業名
    amenity,    -- Amenity type / 設備タイプ
    shop,       -- Shop type / 店舗タイプ
    address,    -- Full address / 住所
    phone,      -- Phone number / 電話番号
    website,    -- Website URL / ウェブサイト
    way         -- Geometry / 幾何情報
)
SELECT
    osm_id,
    name,
    amenity,
    shop,
    COALESCE(tags->'addr:full',''),                  -- Full address fallback / フルアドレスがなければ空文字
    COALESCE(tags->'phone', tags->'contact:phone'), -- Phone fallback / phoneがなければcontact:phone
    tags->'website',
    way
FROM planet_osm_point
WHERE name IS NOT NULL                  -- Must have a name / 名前必須
AND (amenity IS NOT NULL OR shop IS NOT NULL) -- Must have amenity or shop / 設備または店舗がある

-- Handle conflicts on osm_id (update existing rows) / osm_idが重複した場合は更新
ON CONFLICT (osm_id)
DO UPDATE SET
    name = EXCLUDED.name,
    amenity = EXCLUDED.amenity,
    shop = EXCLUDED.shop,
    address = EXCLUDED.address,
    phone = EXCLUDED.phone,
    website = EXCLUDED.website,
    way = EXCLUDED.way;