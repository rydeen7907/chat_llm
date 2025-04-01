"""
物理メモリ監視・解放スクリプト

Python3.13.0

"""

# 各ライブラリのインポート
import gc # ガーベジコレクション
import psutil
import time
import schedule 
import os # プロセッションを終了するため

def release_memory(threshold=65):
    """
    物理メモリの使用量を監視し、一定の閾値を超えた場合にメモリを解放する関数。
    
    Args:
        threshold (int): メモリ使用率の閾値（%）。
    """
    try:
        # 現在のメモリ使用量を取得（MB単位）
        memory_usage = psutil.virtual_memory().percent
        print(f"現在のメモリ使用率: {memory_usage:.2f}%")
        
        if memory_usage > threshold:
            print("メモリ使用率が閾値を超えました。メモリ解放を開始します…")

            # ガーベジコレクションを実行
            gc.collect()
            print("ガーベジコレクションを実行しました。")

            # ※ 参考：必要に応じて、プロセスを再起動するなどの処理を追加できます。
            # 例：特定のプロセスを再起動する場合
            # for proc in psutil.process_iter(['pid', 'name']):
            #     if proc.info['name'] == 'your_process_name':
            #         print(f"プロセス {proc.info['name']} (PID: {proc.info['pid']}) を再起動します...")
            #         os.kill(proc.info['pid'], 9)  # 強制終了
            #         # ここでプロセスを再起動するコマンドを実行
            #         # 例: os.system("your_process_start_command")
            #         break

            # メモリ解放後の使用量を確認
            memory_usage_after = psutil.virtual_memory().percent
            print(f"メモリ解放後のメモリ使用率: {memory_usage_after:.2f}%")
            
        else:
            print("メモリ使用率は閾値以下です。メモリ解放は不要です。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

def main():
    """
    メイン関数。メモリ解放をスケジュールする。
    """
    print("メモリ解放スクリプトを開始します...")

    # メモリ解放をスケジュール（例：5分ごとに実行）
    schedule.every(5).minutes.do(release_memory)

    while True:
        schedule.run_pending()
        time.sleep(1)  # 1秒ごとにスケジュールを確認

if __name__ == "__main__":
    main()
