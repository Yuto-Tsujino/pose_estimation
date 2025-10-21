import sys
import cv2
import time
# ビルドしたモジュールへのパスを追加
sys.path.append('./ximea_bind/build')
import ximea_wrap


# --- 設定 ---
# 使用したいカメラのインデックスを指定
TARGET_CAMERA_INDEX = 2

try:
    print("--- Script for Camera 2 ---")
    
    # 1. 利用可能な全カメラの情報を取得
    available_cameras = ximea_wrap.get_camera_list()
    if TARGET_CAMERA_INDEX >= len(available_cameras):
        print(f"Error: Camera at index {TARGET_CAMERA_INDEX} is not available.")
        exit()

    # 2. 対象のカメラのinstance_pathを取得して初期化
    cam_info = available_cameras[TARGET_CAMERA_INDEX]
    instance_path = cam_info['instance_path']
    
    print(f"Opening Camera {TARGET_CAMERA_INDEX} with path: {instance_path}")
    cam2 = ximea_wrap.XiCam(instance_path)
    
    print("\nCamera 2 is open. Starting acquisition loop...")

    # 3. メインループ：Camera 2 から画像を取得して処理を行う
    while True:
        frame = cam2.grab()
        
        # ここにCamera 2の画像(frame)を使った処理を記述
        # 例：GUI操作、録画など
        # ...

        # 処理結果をウィンドウに表示
        cv2.imshow(f'Camera {TARGET_CAMERA_INDEX} (Module)', frame)

        # 'q'キーが押されたらループを抜ける
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except RuntimeError as e:
    print(f"An error occurred: {e}")

finally:
    cv2.destroyAllWindows()
    print("--- Script for Camera 2 Finished ---")