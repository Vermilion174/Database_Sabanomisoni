from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sys # エラー内容を表示するために追加

app = Flask(__name__)

# データベース接続設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://user:password@localhost:5432/content_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- データベースのモデル定義 ---

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # カスケード削除の設定: カテゴリが消えたら中身も消える
    contents = db.relationship('Content', backref='category', cascade="all, delete")

class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(127), nullable=False)
    memo = db.Column(db.String(255))
    is_owned = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

# --- 初期データ投入 ---
def initialize_db():
    with app.app_context():
        db.create_all()
        # カテゴリが空なら初期データを投入
        if not Category.query.first():
            try:
                defaults = ["アニメ", "漫画", "小説", "映画", "ゲーム"]
                for name in defaults:
                    db.session.add(Category(name=name))
                db.session.commit()
                print("初期データの投入に成功しました。")
            except Exception as e:
                db.session.rollback() # 失敗したら取り消す
                print(f"初期データの投入に失敗しました: {e}", file=sys.stderr)

# --- ルーティング ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 新規コンテンツの保存処理
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        memo = request.form.get('memo')
        is_owned = 'is_owned' in request.form

        if title and category_id:
            # === トランザクション処理開始 ===
            try:
                new_content = Content(title=title, category_id=category_id, memo=memo, is_owned=is_owned)
                db.session.add(new_content)
                db.session.commit() # ここで確定
            except Exception as e:
                db.session.rollback() # エラーが出たら無かったことにする
                print(f"データの追加に失敗しました: {e}", file=sys.stderr)
            # === トランザクション処理終了 ===
            
        return redirect(url_for('index'))

    # --- データの取得とフィルタリング・ソート ---
    filter_category_id = request.args.get('filter_category_id')
    sort_by = request.args.get('sort', 'id')

    query = Content.query

    if filter_category_id:
        query = query.filter_by(category_id=filter_category_id)

    if sort_by == 'title':
        query = query.order_by(Content.title)
    elif sort_by == 'category':
        query = query.join(Category).order_by(Category.name)
    elif sort_by == 'is_owned':
        query = query.order_by(Content.is_owned.desc())
    else:
        query = query.order_by(Content.id.desc())

    contents = query.all()
    categories = Category.query.all()

    return render_template('index.html', contents=contents, categories=categories, 
                           current_filter=filter_category_id, current_sort=sort_by)

@app.route('/delete/<int:id>')
def delete(id):
    # === トランザクション処理開始 ===
    try:
        content = Content.query.get_or_404(id)
        db.session.delete(content)
        db.session.commit() # 削除を確定
    except Exception as e:
        db.session.rollback() # 失敗したら元に戻す
        print(f"削除に失敗しました: {e}", file=sys.stderr)
    # === トランザクション処理終了 ===
    
    return redirect(url_for('index'))

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            # === トランザクション処理開始 ===
            try:
                existing = Category.query.filter_by(name=name).first()
                if not existing:
                    db.session.add(Category(name=name))
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"カテゴリ追加に失敗しました: {e}", file=sys.stderr)
            # === トランザクション処理終了 ===

        return redirect(url_for('manage_categories'))
    
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/delete/<int:id>')
def delete_category(id):
    # === トランザクション処理開始 ===
    try:
        category = Category.query.get_or_404(id)
        # cascade設定により、カテゴリを消すと紐づくコンテンツも自動で消える
        # これら全てが「1つのトランザクション」として処理される
        db.session.delete(category)
        db.session.commit()
    except Exception as e:
        db.session.rollback() # 失敗したらカテゴリもコンテンツも復活（削除取り消し）
        print(f"カテゴリ削除に失敗しました: {e}", file=sys.stderr)
    # === トランザクション処理終了 ===
    
    return redirect(url_for('manage_categories'))

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True, host='0.0.0.0', port=5000)