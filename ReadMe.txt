cd uni_apsamabiso_app(自分で保存した場所)
docker-compose up -d
pip install -r requirements.txt(初めて使用する時のみ)
python app.py
http://localhost:5000

Ctrl+C
docker-compose down
docker-compose down -v(データベースの初期化)
------------------