# # 滤波 + 缺失帧插值 + 动作平滑
#
# import csv
# import sys
# import os
# from collections import defaultdict
#
# import numpy as np
# from scipy.signal import butter, filtfilt
#
#
# # =========================
# # 文件路径
# # =========================
#
# output_dir = sys.argv[2]
#
# input_file = os.path.join(
#     output_dir,
#     "pose_3d_with_2d.csv"
# )
#
# output_file = os.path.join(
#     output_dir,
#     "pose_3d_filtered.csv"
# )
#
#
# # =========================
# # 滤波参数
# # =========================
#
# cutoff = 6.0
# order = 4
#
#
# # =========================
# # 1. 读取原始数据
# # =========================
#
# data = defaultdict(list)
#
# with open(
#     input_file,
#     "r",
#     newline="",
#     encoding="utf-8"
# ) as f:
#
#     reader = csv.DictReader(f)
#
#     for row in reader:
#
#         landmark = row["landmark"]
#
#         data[landmark].append({
#             "frame": int(row["frame"]),
#             "time": float(row["time"]),
#
#             # MediaPipe 3D
#             "x": float(row["x"]),
#             "y": float(row["y"]),
#             "z": float(row["z"]),
#
#             # MediaPipe 2D
#             "image_x": float(row["image_x"]),
#             "image_y": float(row["image_y"])
#         })
#
#
# print("读取完成")
# print("Landmark数量:", len(data))
#
#
# # =========================
# # 2. 自动计算 FPS
# # =========================
#
# first_landmark_rows = next(
#     iter(data.values())
# )
#
# first_landmark_rows.sort(
#     key=lambda item: item["frame"]
# )
#
# if len(first_landmark_rows) < 2:
#
#     raise RuntimeError(
#         "帧数不足，无法计算FPS"
#     )
#
#
# # ---------------------------------------------------------
# # 不再只使用前两个检测成功的帧
# #
# # 因为如果中间正好存在缺帧，
# # 用两个点计算也可以，但这里直接利用整段数据更稳
# # ---------------------------------------------------------
#
# first_frame = first_landmark_rows[0]["frame"]
# last_frame = first_landmark_rows[-1]["frame"]
#
# first_time = first_landmark_rows[0]["time"]
# last_time = first_landmark_rows[-1]["time"]
#
#
# frame_difference = (
#     last_frame - first_frame
# )
#
# time_difference = (
#     last_time - first_time
# )
#
#
# if (
#     frame_difference <= 0
#     or time_difference <= 0
# ):
#
#     raise RuntimeError(
#         "帧号或时间数据异常，无法计算FPS"
#     )
#
#
# fps = (
#     frame_difference
#     / time_difference
# )
#
#
# print(
#     f"自动检测FPS: {fps:.2f}"
# )
#
#
# # =========================
# # 3. 找出完整帧范围
# # =========================
#
# all_existing_frames = sorted(
#     {
#         row["frame"]
#         for rows in data.values()
#         for row in rows
#     }
# )
#
#
# min_frame = min(
#     all_existing_frames
# )
#
# max_frame = max(
#     all_existing_frames
# )
#
#
# full_frames = np.arange(
#     min_frame,
#     max_frame + 1
# )
#
#
# existing_frame_set = set(
#     all_existing_frames
# )
#
#
# missing_frames = [
#     frame
#     for frame in full_frames
#     if frame not in existing_frame_set
# ]
#
#
# print()
# print("=" * 60)
# print("缺失帧检查")
# print("=" * 60)
#
# if missing_frames:
#
#     print(
#         "发现缺失帧:",
#         missing_frames
#     )
#
#     print(
#         "缺失帧数量:",
#         len(missing_frames)
#     )
#
# else:
#
#     print(
#         "没有发现缺失帧"
#     )
#
#
# # =========================
# # 4. 创建 Butterworth 滤波器
# # =========================
#
# b, a = butter(
#     order,
#     cutoff,
#     btype="low",
#     fs=fps
# )
#
#
# # =========================
# # 5. 每个 Landmark：
# #
# # 先插值
# # 再 Butterworth
# # =========================
#
# filtered_rows = []
#
#
# for landmark, rows in data.items():
#
#     rows.sort(
#         key=lambda item: item["frame"]
#     )
#
#
#     # -------------------------
#     # 原始帧号
#     # -------------------------
#
#     frames = np.array(
#         [
#             row["frame"]
#             for row in rows
#         ],
#         dtype=float
#     )
#
#
#     # -------------------------
#     # 原始3D
#     # -------------------------
#
#     x_values = np.array(
#         [
#             row["x"]
#             for row in rows
#         ]
#     )
#
#     y_values = np.array(
#         [
#             row["y"]
#             for row in rows
#         ]
#     )
#
#     z_values = np.array(
#         [
#             row["z"]
#             for row in rows
#         ]
#     )
#
#
#     # -------------------------
#     # 原始2D
#     # -------------------------
#
#     image_x_values = np.array(
#         [
#             row["image_x"]
#             for row in rows
#         ]
#     )
#
#     image_y_values = np.array(
#         [
#             row["image_y"]
#             for row in rows
#         ]
#     )
#
#
#     # =========================
#     # 线性插值补缺帧
#     # =========================
#
#     x_interpolated = np.interp(
#         full_frames,
#         frames,
#         x_values
#     )
#
#     y_interpolated = np.interp(
#         full_frames,
#         frames,
#         y_values
#     )
#
#     z_interpolated = np.interp(
#         full_frames,
#         frames,
#         z_values
#     )
#
#
#     # 2D也需要补齐，
#     # 但仍然不做Butterworth滤波
#
#     image_x_interpolated = np.interp(
#         full_frames,
#         frames,
#         image_x_values
#     )
#
#     image_y_interpolated = np.interp(
#         full_frames,
#         frames,
#         image_y_values
#     )
#
#
#     # =========================
#     # Butterworth滤波
#     # =========================
#
#     x_filtered = filtfilt(
#         b,
#         a,
#         x_interpolated
#     )
#
#     y_filtered = filtfilt(
#         b,
#         a,
#         y_interpolated
#     )
#
#     z_filtered = filtfilt(
#         b,
#         a,
#         z_interpolated
#     )
#
#
#     # =========================
#     # 保存
#     # =========================
#
#     for i, frame in enumerate(
#         full_frames
#     ):
#
#         time_value = (
#             first_time
#             +
#             (
#                 frame - first_frame
#             )
#             / fps
#         )
#
#
#         filtered_rows.append([
#             int(frame),
#             time_value,
#             landmark,
#
#             x_filtered[i],
#             y_filtered[i],
#             z_filtered[i],
#
#             image_x_interpolated[i],
#             image_y_interpolated[i]
#         ])
#
#
#     print(
#         "插值 + 滤波完成:",
#         landmark
#     )
#
#
# # =========================
# # 6. 恢复帧顺序
# # =========================
#
# filtered_rows.sort(
#     key=lambda row: (
#         row[0],
#         row[2]
#     )
# )
#
#
# # =========================
# # 7. 输出 CSV
# # =========================
#
# with open(
#     output_file,
#     "w",
#     newline="",
#     encoding="utf-8"
# ) as f:
#
#     writer = csv.writer(f)
#
#     writer.writerow([
#         "frame",
#         "time",
#         "landmark",
#         "x",
#         "y",
#         "z",
#         "image_x",
#         "image_y"
#     ])
#
#     writer.writerows(
#         filtered_rows
#     )
#
#
# print()
# print("=" * 60)
# print("处理完成")
# print("=" * 60)
#
# print(
#     "补齐缺失帧数量:",
#     len(missing_frames)
# )
#
# print(
#     "最终帧范围:",
#     min_frame,
#     "→",
#     max_frame
# )
#
# print(
#     "输出文件:",
#     output_file
# )

# 3D异常检测 + 缺失帧插值 + Butterworth滤波

import csv
import sys
import os
from collections import defaultdict

import numpy as np
from scipy.signal import butter, filtfilt


# ============================================================
# 文件路径
# ============================================================

output_dir = sys.argv[2]

input_file = os.path.join(
    output_dir,
    "pose_3d_with_2d.csv"
)

output_file = os.path.join(
    output_dir,
    "pose_3d_filtered.csv"
)


# ============================================================
# 参数
# ============================================================

cutoff = 6.0
order = 4


# 用这些点判断“整个人的3D姿态是否突然异常”
# 不使用手腕/手肘，避免网球挥拍造成误判
CHECK_LANDMARKS = [
    "left_shoulder",
    "right_shoulder",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle"
]


# 相邻帧单个关键点3D位移超过这个值，记一次异常
# MediaPipe world坐标单位是m
POINT_JUMP_THRESHOLD = 0.18


# 至少多少个核心点同时异常，
# 才把整帧判定为异常
MIN_ABNORMAL_POINTS = 4


# 异常帧前后额外去掉几帧
# MediaPipe翻转通常不是严格只发生一帧
ABNORMAL_PADDING = 1


# ============================================================
# 1. 读取数据
# ============================================================

data = defaultdict(list)

with open(
    input_file,
    "r",
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        landmark = row["landmark"]

        data[landmark].append({
            "frame": int(row["frame"]),
            "time": float(row["time"]),

            "x": float(row["x"]),
            "y": float(row["y"]),
            "z": float(row["z"]),

            "image_x": float(row["image_x"]),
            "image_y": float(row["image_y"])
        })


print("读取完成")
print("Landmark数量:", len(data))


# ============================================================
# 2. 自动计算 FPS
# ============================================================

first_landmark_rows = next(
    iter(data.values())
)

first_landmark_rows.sort(
    key=lambda item: item["frame"]
)


if len(first_landmark_rows) < 2:

    raise RuntimeError(
        "帧数不足，无法计算FPS"
    )


first_frame = first_landmark_rows[0]["frame"]
last_frame = first_landmark_rows[-1]["frame"]

first_time = first_landmark_rows[0]["time"]
last_time = first_landmark_rows[-1]["time"]


frame_difference = (
    last_frame - first_frame
)

time_difference = (
    last_time - first_time
)


if (
    frame_difference <= 0
    or time_difference <= 0
):

    raise RuntimeError(
        "无法计算FPS"
    )


fps = (
    frame_difference
    / time_difference
)


print(
    f"自动检测FPS: {fps:.2f}"
)


# ============================================================
# 3. 建立 frame → landmark → 坐标
# ============================================================

frame_data = defaultdict(dict)


for landmark, rows in data.items():

    for row in rows:

        frame_data[
            row["frame"]
        ][landmark] = np.array(
            [
                row["x"],
                row["y"],
                row["z"]
            ],
            dtype=float
        )


existing_frames = sorted(
    frame_data.keys()
)


full_frames = np.arange(
    min(existing_frames),
    max(existing_frames) + 1
)


existing_frame_set = set(
    existing_frames
)


# ============================================================
# 4. 找真正“没有识别到人体”的帧
# ============================================================

missing_frames = set(
    int(frame)
    for frame in full_frames
    if frame not in existing_frame_set
)


print()
print("=" * 70)
print("缺失帧")
print("=" * 70)


if missing_frames:

    print(
        sorted(missing_frames)
    )

else:

    print(
        "无"
    )


# ============================================================
# 5. 检测3D异常帧
# ============================================================

abnormal_frames = set()


for i in range(
    1,
    len(existing_frames)
):

    previous_frame = (
        existing_frames[i - 1]
    )

    current_frame = (
        existing_frames[i]
    )


    # --------------------------------------------------------
    # 如果中间本来就有漏检，
    # 不直接跨越缺口比较
    #
    # 比如：
    # 162 → 165
    #
    # 不能把3帧的正常变化当成1帧突变
    # --------------------------------------------------------

    if (
        current_frame
        - previous_frame
        != 1
    ):

        continue


    abnormal_count = 0


    for landmark in CHECK_LANDMARKS:

        if (
            landmark
            not in frame_data[previous_frame]
            or
            landmark
            not in frame_data[current_frame]
        ):

            continue


        p0 = frame_data[
            previous_frame
        ][landmark]

        p1 = frame_data[
            current_frame
        ][landmark]


        distance = np.linalg.norm(
            p1 - p0
        )


        if (
            distance
            > POINT_JUMP_THRESHOLD
        ):

            abnormal_count += 1


    # --------------------------------------------------------
    # 多个身体核心点同时突然变化
    # → 更可能是MediaPipe 3D翻转
    # --------------------------------------------------------

    if (
        abnormal_count
        >= MIN_ABNORMAL_POINTS
    ):

        abnormal_frames.add(
            current_frame
        )

        print(
            f"疑似3D异常: "
            f"Frame {current_frame} | "
            f"{abnormal_count} 个核心点突变"
        )

# ============================================================
# 5.5 处理“漏检后3D姿态错误，随后突然恢复”
#
# 例如：
# 163、164   未识别
# 165～167   重新识别，但3D姿态错误
# 168       突然恢复正常
#
# 如果漏检后的短时间内检测到明显3D突变，
# 就把“漏检结束 → 突变帧”整段视为不可信。
# ============================================================

RECOVERY_SEARCH_FRAMES = 8


for missing_frame in sorted(missing_frames):

    # 只处理一段连续缺失的最后一帧
    if (
        missing_frame + 1
        in missing_frames
    ):
        continue


    missing_end = missing_frame


    # 在漏检结束后的若干帧内寻找3D大突变
    for recovery_frame in range(
        missing_end + 1,
        missing_end + RECOVERY_SEARCH_FRAMES + 1
    ):

        if recovery_frame in abnormal_frames:

            print(
                f"检测到漏检后的3D恢复异常: "
                f"Frame {missing_end + 1}"
                f" → "
                f"{recovery_frame}"
            )

            # 把重新识别后到恢复正常这一段全部判为异常
            for frame in range(
                missing_end + 1,
                recovery_frame + 1
            ):

                abnormal_frames.add(
                    frame
                )

            break

# ============================================================
# 6. 给异常区域增加一点 padding
# ============================================================

expanded_abnormal_frames = set()


for frame in abnormal_frames:

    for offset in range(
        -ABNORMAL_PADDING,
        ABNORMAL_PADDING + 1
    ):

        candidate = (
            frame + offset
        )

        if (
            full_frames[0]
            <= candidate
            <= full_frames[-1]
        ):

            expanded_abnormal_frames.add(
                candidate
            )


# ============================================================
# 7. 合并：
#
# 真正缺帧
# +
# MediaPipe 3D异常帧
# ============================================================

invalid_frames = (
    missing_frames
    |
    expanded_abnormal_frames
)


print()
print("=" * 70)
print("最终需要插值的帧")
print("=" * 70)

print(
    sorted(invalid_frames)
)

print(
    "总数量:",
    len(invalid_frames)
)


# ============================================================
# 8. 创建 Butterworth
# ============================================================

b, a = butter(
    order,
    cutoff,
    btype="low",
    fs=fps
)


# ============================================================
# 9. 每个 Landmark：
#
# 删除异常帧
# → 补齐
# → Butterworth
# ============================================================

filtered_rows = []


for landmark, rows in data.items():

    rows.sort(
        key=lambda item: item["frame"]
    )


    # --------------------------------------------------------
    # 删除已经判定为异常的帧
    # --------------------------------------------------------

    valid_rows = [
        row
        for row in rows
        if row["frame"]
        not in invalid_frames
    ]


    if len(valid_rows) < 10:

        raise RuntimeError(
            f"{landmark} 有效数据太少"
        )


    frames = np.array(
        [
            row["frame"]
            for row in valid_rows
        ],
        dtype=float
    )


    x_values = np.array(
        [
            row["x"]
            for row in valid_rows
        ]
    )

    y_values = np.array(
        [
            row["y"]
            for row in valid_rows
        ]
    )

    z_values = np.array(
        [
            row["z"]
            for row in valid_rows
        ]
    )


    image_x_values = np.array(
        [
            row["image_x"]
            for row in valid_rows
        ]
    )

    image_y_values = np.array(
        [
            row["image_y"]
            for row in valid_rows
        ]
    )


    # ========================================================
    # 10. 插值
    # ========================================================

    x_interpolated = np.interp(
        full_frames,
        frames,
        x_values
    )

    y_interpolated = np.interp(
        full_frames,
        frames,
        y_values
    )

    z_interpolated = np.interp(
        full_frames,
        frames,
        z_values
    )


    image_x_interpolated = np.interp(
        full_frames,
        frames,
        image_x_values
    )

    image_y_interpolated = np.interp(
        full_frames,
        frames,
        image_y_values
    )


    # ========================================================
    # 11. 原来的 Butterworth
    # ========================================================

    x_filtered = filtfilt(
        b,
        a,
        x_interpolated
    )

    y_filtered = filtfilt(
        b,
        a,
        y_interpolated
    )

    z_filtered = filtfilt(
        b,
        a,
        z_interpolated
    )


    # ========================================================
    # 12. 保存
    # ========================================================

    for i, frame in enumerate(
        full_frames
    ):

        time_value = (
            first_time
            +
            (
                frame - first_frame
            )
            / fps
        )


        filtered_rows.append([
            int(frame),
            time_value,
            landmark,

            x_filtered[i],
            y_filtered[i],
            z_filtered[i],

            image_x_interpolated[i],
            image_y_interpolated[i]
        ])


# ============================================================
# 13. 恢复顺序
# ============================================================

filtered_rows.sort(
    key=lambda row: (
        row[0],
        row[2]
    )
)


# ============================================================
# 14. 输出
# ============================================================

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "frame",
        "time",
        "landmark",
        "x",
        "y",
        "z",
        "image_x",
        "image_y"
    ])

    writer.writerows(
        filtered_rows
    )


print()
print("=" * 70)
print("02处理完成")
print("=" * 70)

print(
    "原始缺失帧:",
    sorted(missing_frames)
)

print(
    "检测到的3D异常帧:",
    sorted(abnormal_frames)
)

print(
    "最终插值帧:",
    sorted(invalid_frames)
)

print(
    "输出文件:",
    output_file
)