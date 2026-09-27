import csv
import opensim
import sys
import os


# ============================================================
# 1. 路径
# ============================================================

video_path = sys.argv[1]
output_dir = sys.argv[2]

model_file = os.path.join(
    output_dir,
    "model_with_markers.osim"
)
# 当前视频的数据
input_file = os.path.join(
    output_dir,
    "pose_3d_filtered.csv"
)

output_file = os.path.join(
    output_dir,
    "pose.trc"
)


# ============================================================
# 2. 读取 CSV
# ============================================================

data = {}

with open(input_file, "r", newline="", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        frame = int(row["frame"])

        if frame not in data:
            data[frame] = {
                "time": row["time"]
            }

        name = row["landmark"]

        data[frame][name + "_x"] = row["x"]
        data[frame][name + "_y"] = row["y"]
        data[frame][name + "_z"] = row["z"]


if len(data) < 2:
    raise RuntimeError("有效帧数不足，无法生成TRC")


# ============================================================
# 3. 自动计算 FPS
# ============================================================

sorted_frames = sorted(data)

time_0 = float(
    data[sorted_frames[0]]["time"]
)

time_1 = float(
    data[sorted_frames[1]]["time"]
)

time_difference = time_1 - time_0

if time_difference <= 0:
    raise RuntimeError("视频时间数据异常，无法计算FPS")

fps = 1.0 / time_difference

print(f"自动检测FPS: {fps:.2f}")


# ============================================================
# 4. Marker
# ============================================================

markers = [

    "nose",

    "left_shoulder",
    "right_shoulder",

    "left_elbow",
    "right_elbow",

    "left_wrist",
    "right_wrist",

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
# 5. 自动计算地面高度
# ============================================================

model = opensim.Model(model_file)

model_markers = model.getMarkerSet()


# 用于判断脚底的 Marker
ground_markers = [
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index"
]

lowest_video_y = float("inf")


for frame in data.values():

    for marker_name in ground_markers:

        key = marker_name + "_y"

        if key in frame:

            original_y = float(frame[key])

            opensim_y = -original_y

            if opensim_y < lowest_video_y:
                lowest_video_y = opensim_y


if lowest_video_y == float("inf"):
    raise RuntimeError(
        "没有找到脚部Marker，无法计算高度偏移"
    )


# 给模型脚底留出空间
target_marker_height = 0.05

height_offset = (
    target_marker_height
    - lowest_video_y
)


print("视频最低脚部Marker:", lowest_video_y)
print("目标脚部Marker高度:", target_marker_height)
print("统一高度偏移:", height_offset)


# ============================================================
# 6. 生成 TRC
# ============================================================

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(
        f,
        delimiter="\t",
        lineterminator="\n"
    )


    # --------------------------------------------------------
    # 第一行
    # --------------------------------------------------------

    writer.writerow([
        "PathFileType",
        "4",
        "(X/Y/Z)",
        "pose.trc"
    ])


    # --------------------------------------------------------
    # 第二行
    # --------------------------------------------------------

    writer.writerow([
        "DataRate",
        "CameraRate",
        "NumFrames",
        "NumMarkers",
        "Units",
        "OrigDataRate",
        "OrigDataStartFrame",
        "OrigNumFrames"
    ])


    # --------------------------------------------------------
    # 第三行
    # FPS 不再写死为30
    # --------------------------------------------------------

    writer.writerow([
        f"{fps:.6f}",
        f"{fps:.6f}",
        len(data),
        len(markers),
        "m",
        f"{fps:.6f}",
        "1",
        len(data)
    ])


    # --------------------------------------------------------
    # Marker名称
    # --------------------------------------------------------

    header = [
        "Frame#",
        "Time"
    ]

    for marker in markers:
        header.append(marker)

    writer.writerow(header)


    # --------------------------------------------------------
    # XYZ编号
    # --------------------------------------------------------

    xyz_header = [
        "",
        ""
    ]

    for i in range(len(markers)):

        xyz_header.extend([
            "X" + str(i + 1),
            "Y" + str(i + 1),
            "Z" + str(i + 1)
        ])

    writer.writerow(xyz_header)


    # ========================================================
    # 7. 写入每一帧
    # ========================================================

    for frame in sorted(data):

        row = [
            frame + 1,
            data[frame]["time"]
        ]


        for marker in markers:

            x = float(
                data[frame].get(
                    marker + "_x",
                    "0"
                )
            )

            y = float(
                data[frame].get(
                    marker + "_y",
                    "0"
                )
            )

            z = float(
                data[frame].get(
                    marker + "_z",
                    "0"
                )
            )


            # =================================================
            # MediaPipe → OpenSim 坐标转换
            # =================================================

            opensim_x = z

            opensim_y = -y + height_offset

            opensim_z = x


            row.extend([
                opensim_x,
                opensim_y,
                opensim_z
            ])


        writer.writerow(row)


# ============================================================
# 8. 完成
# ============================================================

print()
print("TRC转换完成")
print("Frames:", len(data))
print("Markers:", len(markers))
print(f"FPS: {fps:.2f}")
print("输出文件:", output_file)

