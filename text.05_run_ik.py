import opensim
import os
import math
import sys

# ============================================================
# 路径
# ============================================================

video_path = sys.argv[1]
output_dir = sys.argv[2]

model_file = os.path.join(
    output_dir,
    "MimicMSK_with_markers.osim"
)

trc_file = os.path.join(
    output_dir,
    "pose.trc"
)

output_motion = os.path.join(
    output_dir,
    "motion_mimic.mot"
)


# ============================================================
# 加载模型
# ============================================================

print()
print("=" * 80)
print("加载 MimicMSK")
print("=" * 80)

model = opensim.Model(
    model_file
)

state = model.initSystem()

coordinates = model.getCoordinateSet()


print(
    "Coordinate 数量:",
    coordinates.getSize()
)


# ============================================================
# 允许 IK 使用的自由度
# ============================================================

active_coordinates = {

    # --------------------------------------------------------
    # 全局 root
    # --------------------------------------------------------

    "root_rx",
    "root_ry",
    "root_rz",

    "root_tx",
    "root_ty",
    "root_tz",


    # --------------------------------------------------------
    # 躯干整体
    # --------------------------------------------------------

    "flex_extension",
    "lat_bending",
    "axial_rotation",


    # --------------------------------------------------------
    # 右腿
    # --------------------------------------------------------

    "hip_flexion_r",
    "hip_adduction_r",
    "hip_rotation_r",

    "knee_angle_r",

    "ankle_angle_r",
    "subtalar_angle_r",


    # --------------------------------------------------------
    # 左腿
    # --------------------------------------------------------

    "hip_flexion_l",
    "hip_adduction_l",
    "hip_rotation_l",

    "knee_angle_l",

    "ankle_angle_l",
    "subtalar_angle_l",


    # --------------------------------------------------------
    # 右肩 / 手臂
    # --------------------------------------------------------

    "elv_angle_r",
    "shoulder_elv_r",
    "shoulder_rot_r",

    "elbow_flex_r",
    "pro_sup_r",

    "deviation_r",
    "flexion_r",


    # --------------------------------------------------------
    # 左肩 / 手臂
    # --------------------------------------------------------

    "elv_angle_l",
    "shoulder_elv_l",
    "shoulder_rot_l",

    "elbow_flex_l",
    "pro_sup_l",

    "deviation_l",
    "flexion_l",
}


# ============================================================
# 锁定不需要的自由度
# ============================================================

print()
print("=" * 80)
print("设置 IK 自由度")
print("=" * 80)


# ============================================================
# 设置 IK 自由度
#
# MimicMSK 有大量约束/从属坐标。
# 不能把所有非主动坐标直接锁死。
#
# 第一版只主动锁：
# 手指等完全不参与 MediaPipe 主体 IK 的自由度。
#
# 膝关节从属坐标、肩胛从属坐标等保持模型原来的设置。
# ============================================================


finger_keywords = [
    "cmc_",
    "mp_",
    "ip_",

    "mcp2_",
    "mcp3_",
    "mcp4_",
    "mcp5_",

    "pm2_",
    "pm3_",
    "pm4_",
    "pm5_",

    "md2_",
    "md3_",
    "md4_",
    "md5_"
]


print()
print("=" * 80)
print("设置 IK 自由度")
print("=" * 80)


for i in range(
    coordinates.getSize()
):

    coord = coordinates.get(i)

    name = coord.getName()


    # --------------------------------------------------------
    # 我们明确要参与 IK 的主自由度
    # --------------------------------------------------------

    if name in active_coordinates:

        coord.setLocked(
            state,
            False
        )

        print(
            f"OPEN   | {name}"
        )

        continue


    # --------------------------------------------------------
    # 手指暂时锁住
    # --------------------------------------------------------

    is_finger = any(
        keyword in name
        for keyword in finger_keywords
    )


    if is_finger:

        coord.setLocked(
            state,
            True
        )

        continue


    # --------------------------------------------------------
    # 其余坐标：
    #
    # 不主动改 locked 状态。
    #
    # 特别是：
    # knee_angle_rotation...
    # knee_angle_translation...
    # shoulder/scapula helper coordinates
    #
    # 让 MimicMSK 自己的约束系统管理。
    # --------------------------------------------------------

    pass


# ============================================================
# root 初始姿态
#
# MimicMSK 原模型是趴着的，
# 我们之前通过 -90° 把它立起来。
#
# IK 的初始值仍然保持这个方向。
# ============================================================

root_rx = coordinates.get(
    "root_rx"
)

root_rx.setValue(
    state,
    math.radians(-90.0),
    False
)


# ============================================================
# 读取 TRC 获取时间范围
# ============================================================

marker_table = opensim.TimeSeriesTableVec3(
    trc_file
)

times = marker_table.getIndependentColumn()


if len(times) == 0:

    raise RuntimeError(
        "pose.trc 中没有数据"
    )


start_time = times[0]
end_time = times[-1]


print()
print("=" * 80)
print("TRC")
print("=" * 80)

print(
    f"开始时间: {start_time:.4f} s"
)

print(
    f"结束时间: {end_time:.4f} s"
)

print(
    f"帧数: {len(times)}"
)


# ============================================================
# 创建 IK Tool
# ============================================================

ik_tool = opensim.InverseKinematicsTool()
ik_tool.set_accuracy(
    1e-4
)

ik_tool.setModel(
    model
)

ik_tool.setMarkerDataFileName(
    trc_file
)

ik_tool.setStartTime(
    start_time
)

ik_tool.setEndTime(
    end_time
)

ik_tool.setOutputMotionFileName(
    output_motion
)


# ============================================================
# Marker Tasks
# ============================================================

task_set = ik_tool.upd_IKTaskSet()


def add_marker_task(
    name,
    weight
):

    task = opensim.IKMarkerTask()

    task.setName(
        name
    )

    task.setApply(
        True
    )

    task.setWeight(
        weight
    )

    task_set.cloneAndAppend(
        task
    )


# ============================================================
# 下肢
#
# 髋膝踝权重大一些
# heel / toe 稍低一点
# ============================================================

add_marker_task(
    "right_hip",
    10.0
)

add_marker_task(
    "left_hip",
    10.0
)

add_marker_task(
    "right_knee",
    10.0
)

add_marker_task(
    "left_knee",
    10.0
)

add_marker_task(
    "right_ankle",
    10.0
)

add_marker_task(
    "left_ankle",
    10.0
)

add_marker_task(
    "right_heel",
    5.0
)

add_marker_task(
    "left_heel",
    5.0
)

add_marker_task(
    "right_foot_index",
    5.0
)

add_marker_task(
    "left_foot_index",
    5.0
)


# ============================================================
# 上肢
# ============================================================

add_marker_task(
    "right_shoulder",
    10.0
)

add_marker_task(
    "left_shoulder",
    10.0
)

add_marker_task(
    "right_elbow",
    10.0
)

add_marker_task(
    "left_elbow",
    10.0
)

add_marker_task(
    "right_wrist",
    10.0
)

add_marker_task(
    "left_wrist",
    10.0
)


print()
print("=" * 80)
print("开始 MimicMSK IK")
print("=" * 80)


# ============================================================
# 运行 IK
# ============================================================

ik_tool.run()


# ============================================================
# 完成
# ============================================================

if os.path.exists(
    output_motion
):

    print()
    print("=" * 80)
    print("MimicMSK IK 完成")
    print("=" * 80)

    print(
        "输出:"
    )

    print(
        output_motion
    )

else:

    raise RuntimeError(
        "IK 运行结束，但没有生成 motion_mimic.mot"
    )