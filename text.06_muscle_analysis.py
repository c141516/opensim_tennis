import opensim
import os
import csv
import math
import sys
import shutil


# ============================================================
# 路径
# ============================================================

video_path = sys.argv[1]
output_dir = sys.argv[2]

source_geometry = (
    r"D:\project\tennis video\pose_model"
    r"\MimicMSK_Model_opensim"
    r"\Geometry"
)

target_geometry = os.path.join(
    output_dir,
    "Geometry"
)

model_file = os.path.join(
    output_dir,
    "MimicMSK_with_markers.osim"
)

motion_file = os.path.join(
    output_dir,
    "motion_mimic.mot"
)

result_dir = os.path.join(
    output_dir,
    "muscle_analysis"
)

os.makedirs(
    result_dir,
    exist_ok=True
)

output_file = os.path.join(
    result_dir,
    "muscle_lengths.csv"
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
muscles = model.getMuscles()


print(
    "Coordinate 数量:",
    coordinates.getSize()
)

print(
    "Muscle 数量:",
    muscles.getSize()
)


# ============================================================
# 读取 motion
# ============================================================

table = opensim.TimeSeriesTable(
    motion_file
)

times = table.getIndependentColumn()
labels = table.getColumnLabels()


print()
print("=" * 80)
print("Motion")
print("=" * 80)

print(
    f"开始时间: {times[0]:.4f} s"
)

print(
    f"结束时间: {times[-1]:.4f} s"
)

print(
    f"帧数: {len(times)}"
)


# ============================================================
# 建立 motion 列名 → Coordinate
# ============================================================

motion_coordinates = []


for i in range(len(labels)):

    name = labels[i]

    try:

        coord = coordinates.get(
            name
        )

        motion_coordinates.append(
            (
                i,
                name,
                coord
            )
        )

    except:

        print(
            f"跳过非 Coordinate 列: {name}"
        )


print()
print(
    "motion 中匹配到的 Coordinate:",
    len(motion_coordinates)
)


# ============================================================
# 肌肉名称
# ============================================================

muscle_names = []


for i in range(
    muscles.getSize()
):

    muscle_names.append(
        muscles.get(i).getName()
    )


# ============================================================
# 输出 CSV
# ============================================================

print()
print("=" * 80)
print("开始计算 Muscle Length")
print("=" * 80)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(
        f
    )


    # --------------------------------------------------------
    # 表头
    # --------------------------------------------------------

    writer.writerow(
        ["time"]
        +
        muscle_names
    )


    # --------------------------------------------------------
    # 每一帧
    # --------------------------------------------------------

    # ========================================================
    # 每一帧
    # ========================================================

    for frame in range(
            len(times)
    ):

        row = table.getRowAtIndex(
            frame
        )

        # ====================================================
        # 设置这一帧 Coordinate
        # ====================================================

        for (
                column_index,
                name,
                coord
        ) in motion_coordinates:

            value = row[
                column_index
            ]

            if (
                    coord.getMotionType()
                    ==
                    opensim.Coordinate.Rotational
            ):
                value = math.radians(
                    value
                )

            coord.setValue(
                state,
                value,
                False
            )

        # ====================================================
        # 满足模型约束
        # ====================================================

        model.assemble(
            state
        )

        model.realizePosition(
            state
        )

        # ====================================================
        # 读取416条肌肉长度
        # ====================================================

        lengths = []

        for i in range(
                muscles.getSize()
        ):
            muscle = muscles.get(i)

            length = (
                muscle
                .getGeometryPath()
                .getLength(state)
            )

            lengths.append(
                length
            )

        # ====================================================
        # 写入当前帧
        # 注意：这里必须在 for frame 循环里面
        # ====================================================

        writer.writerow(
            [
                times[frame]
            ]
            +
            lengths
        )

        if (
                frame % 20 == 0
                or frame == len(times) - 1
        ):
            print(
                f"Frame "
                f"{frame:3d}"
                f"/"
                f"{len(times) - 1}"
                f" 完成"
            )
# ============================================================
# 自动复制 Geometry
# ============================================================

if not os.path.exists(target_geometry):

    print("复制 Geometry...")

    shutil.copytree(
        source_geometry,
        target_geometry
    )

    print("Geometry 复制完成")

else:

    print("Geometry 已存在，跳过复制")

print()
print("=" * 80)
print("Muscle Length 计算完成")
print("=" * 80)

print(
    "输出文件:"
)

print(
    output_file
)