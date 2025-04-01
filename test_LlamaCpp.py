'''
# LLMとチャットするプログラム
Python3.13.0

Streamlitを起動(コマンド入力)
streamlit run "ファイル名".py
'''

# 各ライブラリのインポート
import time 
import re # 正規表現
import gc # ガーベジコレクション
import psutil # プロセッション
import streamlit as st # ストリームリット
import schedule # スケジュール実行
import release_memory # メモリ解放(外部ライブラリとして作成)
import threading
import atexit
from langchain_community.llms import LlamaCpp

# セッション状態を管理するための初期設定
def initialize_session_state():
	if "messages" not in st.session_state:
		st.session_state.messages = []  # 初期化
    # 送信されたトークン数の初期化
		st.session_state.token_sent = 0
    # 受信されたトークン数の初期化    
		st.session_state.token_received = 0
    # レスポンス時間の初期化
		st.session_state.response_time = 0
    # メモリ使用量の初期化
		st.session_state.memory_usage = 0
    # CPU使用量の初期化
		st.session_state.cpu_usage = 0
    # モデルロードのフラグ
		st.session_state.model_loaded = False    

# モデルの準備(ロード)
def load_model(model_path):
    llm = LlamaCpp(model_path=model_path)
    return llm

# モデルを使用して回答を生成
def generate_response(llm, text):
    # プロンプト (例)
    prompt_template= (
        "あなたは誠実かつ優秀な日本人女性のアシスタントです。"
        "指示がない限り常に日本語で回答し、かつ詳細に回答してください。"
        "具体的な例や詳細を挙げて、豊かに説明してください。"
        "どんなに短い回答でも繰り返しを避け、簡潔に回答してください。"
        "回答の先頭に読点(、)や句点(。)などの記号は使用しないでください。"
        "以下がユーザーの質問です。 \n{user_question}"
    )
    
    # ユーザーの質問
    prompt = prompt_template.format(user_question=text)
    
    # 最大トークン数 (最適解が見つからないため要調整)
    max_tokens = 550 
    user_question_length = len(prompt.split())
    if user_question_length > 100:
        max_tokens = 1024 # ex:長い質問の場合は、max_tokensを1024に増やす
    elif user_question_length > 50:
        max_tokens = 768
        
    # 送信されたトークン数を更新
    st.session_state.token_sent += len(prompt.split())
    # 開始時間を記録
    start_time = time.time()
    
    try:
        answer = llm.invoke(prompt, max_tokens=max_tokens)
        # 回答の前後の空白を削除
        answer = re.sub(r"^[、\s]+", "", answer)
        answer = re.sub(r"^[。\s]+", "", answer)
        
        # 終了時間を記録
        end_time = time.time()
        #経過時間
        st.session_state.response_time = end_time - start_time
        # 受信されたトークン数を更新
        st.session_state.token_received += len(answer.split())        
        # メモリ使用量を更新
        st.session_state.memory_usage = psutil.Process().memory_info().rss / 1024 / 1024 # MB
        # CPU使用率を更新
        st.session_state.cpu_usage = psutil.cpu_percent(interval=1) # %
        
        # 物理メモリの消費量が大きいので、実行後にガーベジコレクションを呼び出す
        gc.collect()
        return answer
    
    except Exception as e: 
        return f"エラーが発生しました: {str(e)}"

# UIのメイン部分
def main():
    initialize_session_state()

    # モデルのパスを定義(任意のモデルとファイルパスを指定)
    model_path = " LLM "
    
    # モデルの初期化
    if not st.session_state.model_loaded:
        llm = load_model(model_path)
        st.session_state.model_loaded = True
        st.session_state.llm = llm # モデルの保存
    else:
        llm = st.session_state.llm # モデルの再利用

    # タイトル・コメントはご自由に…
    st.title(" ")
    st.caption(" ")
    st.caption(" ")
    st.caption(" ")
    st.caption(" ")

    if st.button("会話をリセット"):
        st.session_state.messages = []  # 保存された会話をリセット
        st.session_state.response_time = 0
        st.session_state.memory_usage = 0
        st.session_state.cpu_usage = 0
        st.session_state.model_loaded = False # モデルもリセット
        
    st.chat_message("assistant").markdown("何か聞きたいことはありませんか？")
    user_input = st.chat_input("ここにメッセージを入力してください")

    if user_input: 
        st.session_state.messages.append({"role": "user", "content": user_input})       
        st.chat_message("user").markdown(user_input)

        # 直接メッセージを処理
        answer = generate_response(llm, user_input)  # メッセージを処理
        st.session_state.messages.append({"role": "assistant", "content": answer})  
        st.chat_message("assistant").markdown(answer)

    # 過去の会話履歴の表示
    st.subheader("過去の会話履歴")
    MAX_HISTORY_LENGTH = 10
    if len(st.session_state.messages) > MAX_HISTORY_LENGTH:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY_LENGTH:]
    for message in st.session_state.messages:    
        st.chat_message(message["role"]).markdown(message["content"])

    # メトリクス(性能計測)
    st.subheader("メトリクス (参考)")
    st.write(f"レスポンス時間: {st.session_state.response_time:.2f} 秒")
    st.write(f"メモリ使用量: {st.session_state.memory_usage:.2f} MB")
    st.write(f"CPU使用率: {st.session_state.cpu_usage:.2f} %")

# メモリ解放をスケジュールする関数
# def schedule_memory_release():
    # メモリ解放をスケジュール（例：5分ごとに実行）
    # schedule.every(5).minutes.do(release_memory.release_memory, threshold=65)
    # while not stop_event.is_set():
        # schedule.run_pending()
        # time.sleep(1)  # 1秒ごとにスケジュールを確認
        
# スレッドを停止させるためのイベント
stop_event = threading.Event()
    
# スレッドを停止する関数
def stop_mamory_release():
    stop_event.set()
    print("メモリ解放スレッドを停止します…")
    memory_thread.join()
    print("メモリ解放スレッドを停止しました…")

if __name__ == "__main__":    
    # メモリ解放をスレッドで実行
    memory_thread = threading.Thread(target=release_memory.release_memory)
    memory_thread.start()
    # プログラム終了時にスレッドを停止する関数を登録
    atexit.register(stop_mamory_release)
    
    main()