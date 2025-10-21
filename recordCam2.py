# ==============================================================================
#  【決定版】ximea_wrap モジュールを読み込むためのコードブロック
#  今後、XIMEAカメラを使うスクリプトには、このブロックをそのまま貼り付けてください。
# ==============================================================================
import sys
import os

try:
    # このスクリプト自身の絶対パスを取得
    script_path = os.path.abspath(__file__)
    # プロジェクトのルートディレクトリ('Tsujino')を探す
    project_root = script_path
    while os.path.basename(project_root) != 'Tsujino':
        project_root = os.path.dirname(project_root)
        if project_root == os.path.dirname(project_root): # ルートディレクトリまで到達
            raise FileNotFoundError("Project root 'Tsujino' not found.")

    # プロジェクトルートからの絶対パスでモジュールパスを構築
    module_path = os.path.join(project_root, 'pose_estimation', 'ximea_bind', 'build')
    
    # Pythonの検索パスの先頭に、このモジュールパスを追加
    sys.path.insert(0, module_path)
    
    import ximea_wrap
    print(f"Successfully imported 'ximea_wrap' from: {module_path}")

except (ImportError, FileNotFoundError) as e:
    print(f"FATAL ERROR: Could not import 'ximea_wrap'.")
    print(f"Reason: {e}")
    print("Please make sure you have compiled the module and the directory structure is correct.")
    exit()
# ==============================================================================

# これ以降は、パスを気にせず開発できます
import cv2
import time

# --- 設定 ---
TARGET_CAMERA_INDEX = 2
output_dir = os.path.join(project_root, 'videos') # project_root変数をそのまま利用
os.makedirs(output_dir, exist_ok=True)
OUTPUT_FILENAME = os.path.join(output_dir, "recorded_video2.mp4")
FPS = 90.0  # これは「目標」のFPS

video_writer = None

try:
    available_cameras = ximea_wrap.get_camera_list()
    if TARGET_CAMERA_INDEX >= len(available_cameras):
        print(f"Error: Camera at index {TARGET_CAMERA_INDEX} is not available.")
        exit()

    cam_info = available_cameras[TARGET_CAMERA_INDEX]
    instance_path = cam_info['instance_path']
    cam = ximea_wrap.XiCam(instance_path)
    
    # --- FPS計測用の変数を追加 ---
    frame_count = 0
    start_time = time.time()
    
    print(f"\nCamera is open. Press 'q' to stop. Measuring performance...")

    while True:
        frame = cam.grab()
        
        if video_writer is None:
            height, width, _ = frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, FPS, (width, height))
            print("Recording started...")

        video_writer.write(frame)
        cv2.imshow(f'Recording Camera {TARGET_CAMERA_INDEX}', frame)
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except RuntimeError as e:
    print(f"An error occurred: {e}")

finally:
    end_time = time.time()
    elapsed_time = end_time - start_time
    if elapsed_time > 0:
        actual_fps = frame_count / elapsed_time
        print("---------------------------------")
        print(f"  Total Frames: {frame_count}")
        print(f"  Elapsed Time: {elapsed_time:.2f} seconds")
        print(f"  Actual Average FPS: {actual_fps:.2f}")
        print("---------------------------------")

    if video_writer is not None:
        video_writer.release()
        print(f"Recording stopped. Video saved to {OUTPUT_FILENAME}")
    
    cv2.destroyAllWindows()
    print("--- Script Finished ---")