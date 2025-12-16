from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case

app = Flask(__name__)

# データベース接続設定 (docker-composeで設定した情報)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/content_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- データベースのモデル定義 ---

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # カテゴリが削除されたら、紐づくコンテンツも削除する設定 (cascade)
    contents = db.relationship('Content', backref='category', cascade="all, delete")

class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(127), nullable=False) # タイトル最大127文字
    memo = db.Column(db.String(255))                  # メモ最大255文字
    is_owned = db.Column(db.Boolean, default=False)   # 入手済みか否か
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

# --- 初期データ投入 ---
def initialize_db():
    with app.app_context():
        db.create_all()
        # カテゴリが空なら初期データを投入
        if not Category.query.first():
            defaults = ["アニメ", "漫画", "小説", "映画", "ゲーム"]
            for name in defaults:
                db.session.add(Category(name=name))
            db.session.commit()

# --- ルーティング ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 新規コンテンツの保存処理
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        memo = request.form.get('memo')
        is_owned = 'is_owned' in request.form # チェックボックスが入っているか

        if title and category_id:
            new_content = Content(title=title, category_id=category_id, memo=memo, is_owned=is_owned)
            db.session.add(new_content)
            db.session.commit()
        return redirect(url_for('index'))

    # --- データの取得とフィルタリング・ソート ---
    
    # クエリパラメータの取得
    filter_category_id = request.args.get('filter_category_id')
    sort_by = request.args.get('sort', 'id') # デフォルトはID順

    query = Content.query

    # フィルタリング
    if filter_category_id:
        query = query.filter_by(category_id=filter_category_id)

    # ソート (入手済み、カテゴリ、タイトルなどで並び替え)
    if sort_by == 'title':
        query = query.order_by(Content.title)
    elif sort_by == 'category':
        query = query.join(Category).order_by(Category.name)
    elif sort_by == 'is_owned':
        # 入手済みを上に
        query = query.order_by(Content.is_owned.desc())
    else:
        query = query.order_by(Content.id.desc()) # デフォルトは新しい順

    contents = query.all()
    categories = Category.query.all()

    return render_template('index.html', contents=contents, categories=categories, 
                           current_filter=filter_category_id, current_sort=sort_by)

@app.route('/delete/<int:id>')
def delete(id):
    content = Content.query.get_or_404(id)
    db.session.delete(content)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        # カテゴリ追加
        name = request.form.get('name')
        if name:
            existing = Category.query.filter_by(name=name).first()
            if not existing:
                db.session.add(Category(name=name))
                db.session.commit()
        return redirect(url_for('manage_categories'))
    
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/delete/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('manage_categories'))

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True, host='0.0.0.0', port=5000)