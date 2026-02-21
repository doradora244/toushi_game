import pickle
import os

SAVE_PATH = "save_game.pkl"

def save_game(game):
    """ゲームの状態を指定されたパスに保存します"""
    try:
        with open(SAVE_PATH, "wb") as f:
            pickle.dump(game, f)
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game():
    """保存されたゲームの状態を読み込みます"""
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    return None

def delete_save():
    """セーブデータを削除します（リセット用）"""
    if os.path.exists(SAVE_PATH):
        os.remove(SAVE_PATH)
