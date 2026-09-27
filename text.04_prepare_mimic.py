import opensim
import os
import sys


# ============================================================
# 路径
# ============================================================

video_path = sys.argv[1]
output_dir = sys.argv[2]

os.makedirs(
    output_dir,
    exist_ok=True
)
# MimicMSK 原始模型
source_model = (
    r"D:\project\tennis video\pose_model"
    r"\MimicMSK_Model_opensim"
    r"\MimicMSK_OpenSim.osim"
)


# 每个视频文件夹里生成一份项目专用模型
output_model = os.path.join(
    output_dir,
    "MimicMSK_with_markers.osim"
)


# ============================================================
# 加载模型
# ============================================================

print()
print("=" * 80)
print("加载 MimicMSK 模型")
print("=" * 80)

model = opensim.Model(
    source_model
)

state = model.initSystem()

import math

# ============================================================
# 把 MimicMSK 从“趴着”旋转成 OpenSim Y轴向上的站立姿态
# ============================================================

coordinates = model.getCoordinateSet()

root_rx = coordinates.get("root_rx")

root_rx.setDefaultValue(
    math.radians(-90.0)
)

print("已设置 root_rx 默认值: -90°")

body_set = model.getBodySet()
marker_set = model.getMarkerSet()


print(
    "原始 Marker 数量:",
    marker_set.getSize()
)


# ============================================================
# 添加 Marker 的函数
# ============================================================

def add_marker(
    marker_name,
    body_name,
    x,
    y,
    z
):

    # --------------------------------------------------------
    # 如果模型里已经有同名 Marker
    # 就不重复添加
    # --------------------------------------------------------

    for i in range(
        marker_set.getSize()
    ):

        existing_marker = (
            marker_set.get(i)
        )

        if (
            existing_marker.getName()
            == marker_name
        ):

            print(
                f"已存在，跳过: "
                f"{marker_name}"
            )

            return


    body = body_set.get(
        body_name
    )


    marker = opensim.Marker()

    marker.setName(
        marker_name
    )

    marker.connectSocket_parent_frame(
        body
    )

    marker.set_location(
        opensim.Vec3(
            x,
            y,
            z
        )
    )


    model.addMarker(
        marker
    )


    print(
        f"{marker_name:20s}"
        f" -> "
        f"{body_name:12s}"
        f" | "
        f"({x:.4f}, {y:.4f}, {z:.4f})"
    )


# ============================================================
# 添加 MediaPipe 主体 Marker
# ============================================================

print()
print("=" * 80)
print("添加 MediaPipe Markers")
print("=" * 80)


# ============================================================
# 1. 髋关节
#
# MimicMSK 中：
# pelvis → femur
#
# femur 的局部原点就是髋关节附近
# ============================================================

add_marker(
    "right_hip",
    "femur_r",
    0.0,
    0.0,
    0.0
)

add_marker(
    "left_hip",
    "femur_l",
    0.0,
    0.0,
    0.0
)


# ============================================================
# 2. 膝关节
#
# 模型本身已经有：
#
# knee_r -> tibia_r -> (0,0,0)
# knee_l -> tibia_l -> (0,0,0)
#
# 所以直接使用 tibia 原点
# ============================================================

add_marker(
    "right_knee",
    "tibia_r",
    0.0,
    0.0,
    0.0
)

add_marker(
    "left_knee",
    "tibia_l",
    0.0,
    0.0,
    0.0
)


# ============================================================
# 3. 踝关节
#
# 模型已有：
#
# ankle_r -> talus_r -> 0
# ankle_l -> talus_l -> 0
# ============================================================

add_marker(
    "right_ankle",
    "talus_r",
    0.0,
    0.0,
    0.0
)

add_marker(
    "left_ankle",
    "talus_l",
    0.0,
    0.0,
    0.0
)


# ============================================================
# 4. 脚跟
#
# calcn 的原点不一定就是脚后跟表面，
# 所以第一版给一个轻微向后的偏移。
#
# 后面可以根据 OpenSim GUI 实际位置微调。
# ============================================================

# 直接复制 MimicMSK 原生 RCAL / LCAL

add_marker(
    "right_heel",
    "calcn_r",
    -0.030,
    -0.020,
    0.0
)

add_marker(
    "left_heel",
    "calcn_l",
    -0.030,
    -0.020,
    0.0
)


# ============================================================
# 5. 脚尖
#
# 模型原本已有：
#
# RTOE:
# calcn_r
# (0.205, 0.0297, -0.03)
#
# LTOE:
# calcn_l
# (0.205, 0.0297, 0.03)
#
# 我们直接使用模型自己已有的脚尖位置。
# ============================================================

add_marker(
    "right_foot_index",
    "calcn_r",
    0.205,
    0.0297,
    -0.030
)

add_marker(
    "left_foot_index",
    "calcn_l",
    0.205,
    0.0297,
    0.030
)


# ============================================================
# 6. 肩关节
#
# humerus 的局部原点位于肩关节附近。
#
# MediaPipe shoulder 更接近肩关节中心，
# 所以第一版使用 humerus 原点。
# ============================================================

add_marker(
    "right_shoulder",
    "humerus_r",
    0.0,
    0.0,
    0.0
)

add_marker(
    "left_shoulder",
    "humerus_l",
    0.0,
    0.0,
    0.0
)


# ============================================================
# 7. 肘关节
#
# 模型的 ulna 原点位于肘附近。
# ============================================================

add_marker(
    "right_elbow",
    "ulna_r",
    0.0,
    0.0,
    0.0
)

add_marker(
    "left_elbow",
    "ulna_l",
    0.0,
    0.0,
    0.0
)


# ============================================================
# 8. 手腕
#
# MimicMSK 中：
# radius → lunate
#
# lunate 原点相当接近腕关节中心。
# ============================================================

add_marker(
    "right_wrist",
    "lunate_r",
    0.0,
    0.0,
    0.0
)

add_marker(
    "left_wrist",
    "lunate_l",
    0.0,
    0.0,
    0.0
)


# ============================================================
# 重新初始化模型
# ============================================================

model.finalizeConnections()

state = model.initSystem()

# ============================================================
# 自动把模型移动到地面
# ============================================================

model.finalizeConnections()
state = model.initSystem()
model.realizePosition(state)

marker_set = model.getMarkerSet()

foot_markers = [
    marker_set.get("right_heel"),
    marker_set.get("left_heel"),
    marker_set.get("right_foot_index"),
    marker_set.get("left_foot_index")
]


foot_y_values = []

for marker in foot_markers:

    pos = marker.getLocationInGround(state)

    foot_y_values.append(
        pos.get(1)
    )


lowest_y = min(
    foot_y_values
)

ground_offset = -lowest_y


print()
print("=" * 80)
print("Ground alignment")
print("=" * 80)

print(
    f"最低脚点 Y: {lowest_y:.4f} m"
)

print(
    f"需要上移: {ground_offset:.4f} m"
)


# ============================================================
# 修改整个模型的 root_ty
# ============================================================

coordinates = model.getCoordinateSet()

root_ty = coordinates.get(
    "root_ty"
)

old_root_ty = root_ty.getDefaultValue()

root_ty.setDefaultValue(
    old_root_ty + ground_offset
)


print(
    f"root_ty: "
    f"{old_root_ty:.4f}"
    f" → "
    f"{old_root_ty + ground_offset:.4f}"
)


# ============================================================
# 重新初始化
# ============================================================

model.finalizeConnections()
state = model.initSystem()
model.realizePosition(state)
# ============================================================
# 保存
# ============================================================

print()
print("=" * 80)
print("保存 MimicMSK 项目模型")
print("=" * 80)

model.printToXML(
    output_model
)


print(
    "输出文件:"
)

print(
    output_model
)


print()
print(
    "新 Marker 数量:",
    model.getMarkerSet().getSize()
)

print()
print("=" * 80)
print("text04 完成")
print("=" * 80)