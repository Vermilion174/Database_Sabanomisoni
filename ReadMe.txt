cd uni_apsamabiso_app(自分で保存した場所)
docker-compose up -d
pip install -r requirements.txt(初めて使用する時のみ)
python app.py
http://localhost:5000

Ctrl+C
docker-compose down
docker-compose down -v(データベースの初期化)
------------------

# 📚 積みコン（TsumiCon）

気になっているコンテンツを「積みタスク」のように管理できる Flask 製 Web アプリです。  
アニメ・漫画・小説・映画・ゲームなど、ジャンルごとに整理しながら「積み」を可視化できます。

---

## ✨ 特徴

- 初期カテゴリ（アニメ / 漫画 / 小説 / 映画 / ゲーム）を自動生成
- カテゴリの追加・削除
- コンテンツ（タイトル・メモ・所持フラグ）の登録
- カテゴリ別フィルタリング
- タイトル / カテゴリ / 所持フラグ / 登録順でソート
- カテゴリ削除時は紐づくコンテンツも自動削除（カスケード）
- 追加・削除時はトランザクション処理で安全に操作

---

## 🛠 技術スタック

- Python 3.x
- Flask
- Flask SQLAlchemy
- PostgreSQL（psycopg2）
- HTML（Jinja2 テンプレート）

---

## 📦 セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/yourname/tsumicon.git
cd tsumicon
