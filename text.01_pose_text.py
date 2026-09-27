# #视频用mediapipe识别关键点
#
# import cv2
# import mediapipe as mp
# import csv
#
# model_path = r"D:\project\tennis video\pose_model\pose_landmarker_full.task"
#
# BaseOptions = mp.tasks.BaseOptions
# PoseLandmarker = mp.tasks.vision.PoseLandmarker
#
# options = mp.tasks.vision.PoseLandmarkerOptions(
#     base_options=BaseOptions(model_asset_path=model_path)
# )
#
# detector = PoseLandmarker.create_from_options(options)
#
# video_path = r"D:\project\tennis video\video\video tem.mp4"
#
# cap = cv2.VideoCapture(video_path)
# fps = cap.get(cv2.CAP_PROP_FPS)
#
# data = []
# frame_count = 0
#
# landmark_names = [
#     "nose",
#     "left_eye_inner",
#     "left_eye",
#     "left_eye_outer",
#     "right_eye_inner",
#     "right_eye",
#     "right_eye_outer",
#     "left_ear",
#     "right_ear",
#     "mouth_left",
#     "mouth_right",
#     "left_shoulder",
#     "right_shoulder",
#     "left_elbow",
#     "right_elbow",
#     "left_wrist",
#     "right_wrist",
#     "left_pinky",
#     "right_pinky",
#     "left_index",
#     "right_index",
#     "left_thumb",
#     "right_thumb",
#     "left_hip",
#     "right_hip",
#     "left_knee",
#     "right_knee",
#     "left_ankle",
#     "right_ankle",
#     "left_heel",
#     "right_heel",
#     "left_foot_index",
#     "right_foot_index"
# ]
#
# while True:
#     ret, frame = cap.read()
#
#     if not ret:
#         break
#
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#     mp_image = mp.Image(
#         image_format=mp.ImageFormat.SRGB,
#         data=rgb_frame
#     )
#      #将cv的图片换成mediapipe可以用的格式
#
#     result = detector.detect(mp_image)#**图片交给detector，去处理
#
#     landmarks = result.pose_landmarks[0]
#     world_landmarks = result.pose_world_landmarks[0]
#
#     h, w, _ = frame.shape
#
#     connections = [
#         (0, 7),
#         (0, 8),
#         (11, 13),
#         (13, 15),
#         (12, 14),
#         (14, 16),
#         (11, 12),
#         (11, 23),
#         (12, 24),
#         (23, 24),
#         (23, 25),
#         (25, 27),
#         (24, 26),
#         (26, 28)
#     ]
#
#     for i, world_landmark in enumerate(world_landmarks):
#         # 同一个关键点在视频画面中的2D结果
#         image_landmark = landmarks[i]
#
#         data.append([
#             frame_count,
#             frame_count / fps,
#             landmark_names[i],
#
#             # MediaPipe world 3D坐标
#             world_landmark.x,
#             world_landmark.y,
#             world_landmark.z,
#
#             # 视频画面中的归一化2D坐标
#             image_landmark.x,
#             image_landmark.y,
#
#             # 这个点当前有多可信/可见
#             image_landmark.visibility
#         ])
#     frame_count += 1
#
#     for i, landmark in enumerate(landmarks):
#
#         x = int(landmark.x * w)
#         y = int(landmark.y * h)
#
#         cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
#
#     for start, end in connections:
#         start_point = landmarks[start]
#         end_point = landmarks[end]
#
#         x1 = int(start_point.x * w)
#         y1 = int(start_point.y * h)
#
#         x2 = int(end_point.x * w)
#         y2 = int(end_point.y * h)
#
#         cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
#
#     cv2.namedWindow("window1", cv2.WINDOW_NORMAL)
#     cv2.resizeWindow("window1", 500, 850)
#     cv2.imshow("window1", frame)
#     key = cv2.waitKey(30)  # 先处理窗口信息，后面再判断两个关闭的条件
#     if key != -1:
#         break
#     if cv2.getWindowProperty("window1", cv2.WND_PROP_VISIBLE) < 1:
#         break
#
#
# cap.release()
# cv2.destroyAllWindows()
#
# output_path = r"D:\project\tennis video\data\pose_3d_with_2d.csv"
#
# with open(output_path, "w", newline="", encoding="utf-8") as f:
#
#     writer = csv.writer(f)
#
#     writer.writerow([
#         "frame",
#         "time",
#         "landmark",
#
#         "x",
#         "y",
#         "z",
#
#         "image_x",
#         "image_y",
#
#         "visibility"
#     ])
#
#     writer.writerows(data)
#

# ============================================================
# text.01_pose_text.py
# 功能：
# 视频 → MediaPipe Pose → 3D + 2D关键点CSV
# ============================================================

import cv2
import mediapipe as mp
import csv
import time
import sys
import os

# ============================================================
# 1. 路径
# ============================================================

model_path = r"D:\project\tennis video\pose_model\pose_landmarker_full.task"

# run_all.py 传进来的参数
video_path = sys.argv[1]
output_dir = sys.argv[2]

# 本步骤输出文件
output_path = os.path.join(
    output_dir,
    "pose_3d_with_2d.csv"
)

# ============================================================
# 2. 创建 MediaPipe PoseLandmarker
# ============================================================

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker

options = mp.tasks.vision.PoseLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=model_path
    )
)

detector = PoseLandmarker.create_from_options(options)


# ============================================================
# 3. MediaPipe 33个关键点名称
# ============================================================

landmark_names = [
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index"
]


# ============================================================
# 4. 打开视频
# ============================================================

cap = cv2.VideoCapture(video_path)

# 检查视频是否成功打开
if not cap.isOpened():
    raise RuntimeError(
        f"无法打开视频：{video_path}"
    )

# 获取视频帧率
fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    raise RuntimeError(
        f"无法获取视频FPS：{video_path}"
    )


# ============================================================
# 5. 准备数据
# ============================================================

data = []

frame_count = 0
start_time = time.time()

# ============================================================
# 6. 逐帧处理视频
# ============================================================

while True:

    # 读取一帧
    ret, frame = cap.read()

    # 视频读完
    if not ret:
        break


    # --------------------------------------------------------
    # OpenCV：BGR
    # 转成 MediaPipe 使用的 RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # OpenCV图片 → MediaPipe图片
    # --------------------------------------------------------

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # --------------------------------------------------------
    # MediaPipe姿态识别
    # --------------------------------------------------------

    result = detector.detect(mp_image)


    # --------------------------------------------------------
    # 如果这一帧没有识别到人体
    # 就跳过这一帧
    # --------------------------------------------------------

    if (
        not result.pose_landmarks
        or not result.pose_world_landmarks
    ):
        print(
            f"警告：第 {frame_count} 帧未识别到人体"
        )

        frame_count += 1
        continue


    # --------------------------------------------------------
    # 2D关键点
    # --------------------------------------------------------

    landmarks = result.pose_landmarks[0]


    # --------------------------------------------------------
    # 3D world关键点
    # --------------------------------------------------------

    world_landmarks = result.pose_world_landmarks[0]


    # --------------------------------------------------------
    # 保存这一帧33个关键点
    # --------------------------------------------------------

    for i, world_landmark in enumerate(world_landmarks):

        image_landmark = landmarks[i]

        data.append([
            frame_count,

            # 当前时间（秒）
            frame_count / fps,

            landmark_names[i],

            # MediaPipe 3D world坐标
            world_landmark.x,
            world_landmark.y,
            world_landmark.z,

            # 视频画面中的2D归一化坐标
            image_landmark.x,
            image_landmark.y,

            # 关键点可见度
            image_landmark.visibility
        ])


    frame_count += 1


# ============================================================
# 7. 释放视频
# ============================================================
end_time = time.time()

cap.release()

detector.close()

print(f"总耗时：{end_time - start_time:.2f} 秒")
print(f"平均每帧：{(end_time - start_time) / frame_count:.3f} 秒")

# ============================================================
# 8. 保存CSV
# ============================================================

with open(
    output_path,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    # 表头
    writer.writerow([
        "frame",
        "time",
        "landmark",

        "x",
        "y",
        "z",

        "image_x",
        "image_y",

        "visibility"
    ])

    # 所有关键点数据
    writer.writerows(data)


# ============================================================
# 9. 完成
# ============================================================

print()
print("MediaPipe关键点提取完成")
print(f"视频帧数：{frame_count}")
print(f"视频FPS：{fps:.2f}")
print(f"保存位置：{output_path}")