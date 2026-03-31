# Telepo_etl
# 🗺️ Tokyo Business Search System

A location-based business search application built using **OpenStreetMap (OSM), PostGIS, and Streamlit**.
This system allows users to search for nearby businesses (e.g., cafes, clinics) around train stations in Tokyo.

---

# 🚀 Features

* 🔍 Search businesses by keyword (English / Japanese)
* 📍 Station-based location search
* 🗺️ Interactive map visualization (Folium)
* 📊 Tabular results with business details
* 🔄 Manual data update pipeline (OSM → DB)
* ⚡ Fast geospatial queries using PostGIS

---

# 🧱 System Architecture

```
           OpenStreetMap (Geofabrik)
                     ↓
            osm2pgsql (ETL)
                     ↓
               PostGIS DB
                     ↓
           SQL Queries (search)
                     ↓
              Streamlit App
```

---

# 🧠 Why This Architecture?

### ❌ Why NOT direct OSM API?

* Slow (network latency)
* Rate-limited
* Not production-safe

### ✅ Why DB + ETL?

* ⚡ Fast (local indexed queries)
* 🔁 Reliable (no external dependency)
* 🔍 Advanced filtering (distance, tags)
* 📊 Scalable for large datasets

---

# 🛠️ Tech Stack

| Component        | Technology                |
| ---------------- | ------------------------- |
| Backend DB       | PostgreSQL + PostGIS      |
| Data Source      | OpenStreetMap (Geofabrik) |
| ETL              | osm2pgsql                 |
| Frontend         | Streamlit                 |
| Maps             | Folium                    |
| Containerization | Docker                    |

---

# 📦 Prerequisites

Install the following:

### 1. Docker Desktop

https://www.docker.com/products/docker-desktop

### 2. Python (3.10+ recommended)

https://www.python.org/downloads/

---

# 📥 Project Setup

## 1. Clone Repository

```bash
git clone https://github.com/PetrichorPallavi/Telepo_etl.git
cd tokyo-osm-system
```

---

## 2. Download OSM Data

Download Kanto region data:

👉 https://download.geofabrik.de/asia/japan/kanto-latest.osm.pbf

Place file in:

```
/data/kanto-latest.osm.pbf
```

---

## 3. Start Docker Services

```bash
docker compose up -d
```

This will start:

* PostGIS database
* OSM importer
* OSM updater

---

## 4. Initialize Database (First Time Only)

Import OSM data:

```bash
docker compose run osm_import
```

---

## 5. Create Business Table

Run SQL:

```bash
docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/create_business_table.sql
```

---

## 6. Refresh Business Data

```bash
docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/refresh_business_table.sql
```

---

## 7. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 8. Run Application

```bash
cd app
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

---

# 🔄 Updating Data

You can update OSM data using:

### Option A — Manual Script

```powershell
.\update.ps1
```

### Option B — UI Button (Recommended)

* Click **"Update Data"** in sidebar
* Automatically:

  * Fetches latest OSM updates
  * Refreshes business table
  * Updates timestamp

---

# 📁 Project Structure

```
tokyo-osm-system/
│
├── app/
│   ├── app.py
│   └── queries.py
│
├── sql/
│   ├── create_business_table.sql
│   └── refresh_business_table.sql
│
├── data/
│   └── kanto-latest.osm.pbf
│
├── docker-compose.yml
├── update.ps1
└── README.md
```

---

# ⚙️ Configuration

### Database Connection (app/queries.py)

```python
postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm
```

Ensure Docker is mapped to port **5433**.

---

# ⚠️ Troubleshooting

## ❌ DB Connection Timeout

```bash
docker compose up -d
```

---

## ❌ Port Conflict

Change in `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"
```

---

## ❌ SQL File Not Found in Container

Ensure:

```yaml
volumes:
  - ./sql:/sql
```

---

## ❌ PowerShell Script Blocked

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

# 🚀 Future Improvements

* 🔍 Fuzzy search / autocomplete
* 🇯🇵 Japanese-English keyword normalization
* 📄 Pagination / infinite scroll
* ⚡ Query optimization (indexes, caching)
* 🧠 Ranking (distance + popularity)

---

# 📌 Notes

* Phone availability depends on OSM data completeness
* Not all businesses have full metadata

---

# 👨‍💻 Author

Developed as a geospatial search system prototype using real-world OSM data.

---

# 📄 License


# Telepo_etl

# 🗺️ 東京ビジネス検索システム

本システムは、**OpenStreetMap（OSM）、PostGIS、Streamlit** を用いて構築された、位置情報ベースのビジネス検索アプリケーションです。
東京の各駅周辺にある店舗（例：カフェ、クリニックなど）を検索することができます。

---

# 🚀 機能

* 🔍 キーワード検索（英語／日本語対応）
* 📍 駅を基準とした位置検索
* 🗺️ インタラクティブな地図表示（Folium）
* 📊 店舗情報の一覧表示（テーブル形式）
* 🔄 手動データ更新パイプライン（OSM → DB）
* ⚡ PostGISによる高速な地理空間検索

---

# 🧱 システム構成

```
           OpenStreetMap (Geofabrik)
                     ↓
            osm2pgsql (ETL)
                     ↓
               PostGIS DB
                     ↓
           SQLクエリ（検索）
                     ↓
             Streamlitアプリ
```

---

# 🧠 この構成を採用した理由

## ❌ OSM APIを直接使用しない理由

* 処理が遅い（ネットワーク遅延）
* レート制限がある
* 本番環境での安定性に欠ける

## ✅ DB + ETLを採用する理由

* ⚡ 高速（ローカルでインデックス検索）
* 🔁 安定（外部依存なし）
* 🔍 高度な検索（距離・タグ条件）
* 📊 大規模データにも対応可能

---

# 🛠️ 技術スタック

| コンポーネント  | 技術                       |
| -------- | ------------------------ |
| バックエンドDB | PostgreSQL + PostGIS     |
| データソース   | OpenStreetMap（Geofabrik） |
| ETL      | osm2pgsql                |
| フロントエンド  | Streamlit                |
| 地図表示     | Folium                   |
| コンテナ     | Docker                   |

---

# 📦 事前準備

以下をインストールしてください。

## 1. Docker Desktop

[https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

## 2. Python（3.10以上推奨）

[https://www.python.org/downloads/](https://www.python.org/downloads/)

---

# 📥 プロジェクトセットアップ

## 1. リポジトリのクローン

```bash
git clone https://github.com/PetrichorPallavi/Telepo_etl.git
cd tokyo-osm-system
```

---

## 2. OSMデータのダウンロード

関東地方のデータをダウンロード：

👉 [https://download.geofabrik.de/asia/japan/kanto-latest.osm.pbf](https://download.geofabrik.de/asia/japan/kanto-latest.osm.pbf)

以下のディレクトリに配置：

```
/data/kanto-latest.osm.pbf
```

---

## 3. Dockerサービスの起動

```bash
docker compose up -d
```

以下が起動します：

* PostGISデータベース
* OSMインポーター
* OSMアップデーター

---

## 4. データベース初期化（初回のみ）

OSMデータをインポート：

```bash
docker compose run osm_import
```

---

## 5. ビジネステーブルの作成

SQLを実行：

```bash
docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/setup.sql
```
や
```bash
Get-Content sql/setup.sql | docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm
```
や
```bash
type sql/setup.sql | docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm
```
---

## 6. ビジネスデータの更新

```bash
docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/refresh_business_table.sql
```
や
```bash
Get-Content sql/refresh_business_table.sql | docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm
```
や
```bash
type sql/refresh_business_table.sql | docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm

---

## 7. Python依存関係のインストール

```bash
pip install -r requirements.txt
```

---

## 8. アプリケーションの起動

```bash
cd app
streamlit run app.py
```

ブラウザで以下を開く：

```
http://localhost:8501
```

---

# 🔄 データ更新

OSMデータは以下の方法で更新できます：

## 方法A — 手動スクリプト

```powershell
.\update.ps1
```

---

## 方法B — UIボタン（推奨）

* サイドバーの **「Update Data」** をクリック
* 自動的に以下を実行：

  * 最新OSMデータの取得
  * ビジネステーブルの更新
  * 更新時刻の記録

---

# 📁 プロジェクト構成

```
tokyo-osm-system/
│
├── app/
│   ├── app.py
│   └── queries.py
│   └── chek_encoding.py
│   └── db.py
│
├── sql/
│   ├── setup.sql
│   └── refresh_business_table.sql
│
├── data/
│   └── kanto-latest.osm.pbf
|   └── state.txt
|
├── etl/
│   └── update.sh
|   └── update_and_refresh.sh
│
├── docker-compose.yml
├── update.ps1
└── README.md
```

---

# ⚙️ 設定

## データベース接続（app/queries.py）

```python
postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm
```

Dockerが **ポート5433** にマッピングされていることを確認してください。

---

# ⚠️ トラブルシューティング

## ❌ DB接続タイムアウト

```bash
docker compose up -d
```

---

## ❌ ポート競合

`docker-compose.yml` を変更：

```yaml
ports:
  - "5433:5432"
```

---

## ❌ コンテナ内でSQLファイルが見つからない

以下を確認：

```yaml
volumes:
  - ./sql:/sql
```

---

## ❌ PowerShellスクリプトが実行できない

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

# 🚀 今後の改善点

* 🔍 あいまい検索／オートコンプリート
* 🇯🇵 日英キーワードの正規化
* 📄 ページネーション／無限スクロール
* ⚡ クエリ最適化（インデックス・キャッシュ）
* 🧠 ランキング機能（距離＋人気度）

---

# 📌 注意事項

* 電話番号の有無はOSMデータの内容に依存します
* すべての店舗に完全な情報があるとは限りません

---

# 👨‍💻 作者

実際のOSMデータを用いた地理空間検索システムのプロトタイプとして開発。

---

# 📄 ライセンス
