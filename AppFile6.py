import streamlit as st
import sqlite3
import datetime

# SQLiteデータベースに接続
conn = sqlite3.connect('bulletin_board2.db')
c = conn.cursor()

# テーブルを作成する関数
def create_table():
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        message TEXT, 
        date TEXT)
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS deleted_posts
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        message TEXT, 
        date TEXT, 
        deleted_at TEXT)
    ''')
    conn.commit()

# 投稿データをデータベースに保存する関数
def add_post(name, message):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO posts (name, message, date) VALUES (?, ?, ?)', (name, message, date))
    conn.commit()

# データベースから投稿データを取得する関数
def get_posts():
    c.execute('SELECT id, name, message, date FROM posts ORDER BY id DESC')
    return c.fetchall()

# 削除された投稿を削除ログに追加する関数
def log_deleted_post(post_id, name, message, date):
    deleted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO deleted_posts (id, name, message, date, deleted_at) VALUES (?, ?, ?, ?, ?)', 
              (post_id, name, message, date, deleted_at))
    conn.commit()

# 特定の投稿を削除する関数
def delete_post(post_id):
    # 削除対象の投稿を取得
    c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    
    # 削除ログに保存
    if post:
        log_deleted_post(post[0], post[1], post[2], post[3])
    
    # 元の投稿を削除
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()

# 削除された投稿の履歴を取得する関数
def get_deleted_posts():
    c.execute('SELECT id, name, message, date, deleted_at FROM deleted_posts ORDER BY deleted_at DESC')
    return c.fetchall()

# テーブル作成
create_table()

# 管理者認証
st.sidebar.title("管理者ログイン")
admin_password = st.sidebar.text_input("パスワード", type="password")
is_admin = False

# 簡単なパスワード認証（パスワードは 'admin99' に設定）
if admin_password == 'admin99':
    is_admin = True
    st.sidebar.success("管理者としてログインしました。")
else:
    if admin_password:
        st.sidebar.error("パスワードが間違っています。")

# サイドバーに投稿フォームを作成
st.sidebar.title("掲示板に投稿する")
name = st.sidebar.text_input("名前")
message = st.sidebar.text_area("メッセージ")
submit_button = st.sidebar.button("投稿")

# 投稿ボタンが押されたときの処理
if submit_button:
    if name and message:
        # データベースに投稿を追加
        add_post(name, message)
        st.sidebar.success("投稿が完了しました！")
    else:
        st.sidebar.error("名前とメッセージを入力してください。")

# メインエリアに投稿リストを表示
st.title("掲示板")
st.write("この掲示板サイトはとあるプログラミング初心者が作ったサイトです。")
st.write("投稿は自由にしてもらって構いませんが、公序良俗に反するような投稿は削除させていただきます。")
posts = get_posts()
if posts:
    for post in posts:
        post_id = post[0]
        st.write(f"**{post[1]}** ({post[3]})")
        st.write(post[2])
        # 管理者でログインしている場合のみ削除ボタンを表示
        if is_admin:
            if st.button(f"この投稿を削除", key=f"delete_{post_id}"):
                delete_post(post_id)
                st.success(f"投稿ID {post_id} が削除されました。")
                st.experimental_rerun()  # ページを再読み込みして、削除後の状態を反映
        st.markdown("---")
else:
    st.write("まだ投稿がありません。")

# 管理者のみ、削除ログを表示
if is_admin:
    st.title("削除された投稿の履歴")
    deleted_posts = get_deleted_posts()
    if deleted_posts:
        for deleted_post in deleted_posts:
            st.write(f"**{deleted_post[1]}** ({deleted_post[3]}) - {deleted_post[4]} に削除")
            st.write(deleted_post[2])
            st.markdown("---")
    else:
        st.write("削除された投稿はありません。")
