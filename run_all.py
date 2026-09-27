import subprocess
import sys
import os
import time
import tkinter as tk
from tkinter import filedialog
import shutil

# =========================
# 基础路径
# =========================

code_dir = os.path.dirname(
    os.path.abspath(__file__)
)

python_exe = sys.executable


# =========================
# 选择视频
# =========================

root = tk.Tk()
root.withdraw()

video_path = filedialog.askopenfilename(
    title="选择网球视频",
    filetypes=[
        ("视频文件", "*.mp4 *.avi *.mov *.mkv"),
        ("所有文件", "*.*")
    ]
)

root.destroy()

if not video_path:
    print("未选择视频")
    sys.exit(0)

print(f"选择的视频：{video_path}")


# =========================
# 给视频创建独立结果文件夹
# =========================

video_name = os.path.splitext(
    os.path.basename(video_path)
)[0]

data_dir = r"D:\project\tennis video\data"

output_dir = os.path.join(
    data_dir,
    video_name
)

os.makedirs(
    output_dir,
    exist_ok=True
)

# 把 OpenSim 模型复制到当前视频结果文件夹

source_model = r"D:\project\tennis video\data\model_with_markers.osim"

output_model = os.path.join(
    output_dir,
    "model_with_markers.osim"
)

shutil.copy2(
    source_model,
    output_model
)

print(f"模型已复制：{output_model}")

print(f"结果文件夹：{output_dir}")


# =========================
# 五个处理程序
# =========================

scripts = [
    "text.01_pose_text.py",
    "text.02_new.py",
    "text.03_csv_to_trc.py",
    "text.04_prepare_mimic.py",
    "text.05_run_ik.py",
    "text.06_muscle_analysis.py"
]


print("=" * 60)
print("Tennis Video -> OpenSim")
print("=" * 60)

total_start = time.time()


# =========================
# 依次运行
# =========================

for i, script in enumerate(
    scripts,
    start=1
):

    script_path = os.path.join(
        code_dir,
        script
    )

    print()
    print(
        f"[{i}/{len(scripts)}] "
        f"正在运行: {script}"
    )


    if not os.path.exists(script_path):

        print(
            f"找不到文件: {script_path}"
        )

        sys.exit(1)


    step_start = time.time()


    # 把视频路径和结果文件夹
    # 传给每一个处理程序

    result = subprocess.run(
        [
            python_exe,
            script_path,
            video_path,
            output_dir
        ]
    )


    step_end = time.time()


    if result.returncode != 0:

        print()
        print(
            f"{script}运行失败"
        )

        print("流程结束")

        sys.exit(
            result.returncode
        )


    print(
        f"{script}完成 "
        f"耗时："
        f"{step_end - step_start:.2f} 秒"
    )


# =========================
# 完成
# =========================

total_end = time.time()


print()
print("=" * 60)
print("全部流程运行完成")
print(
    f"总耗时："
    f"{total_end - total_start:.2f} 秒"
)
print("最终结果：")
print(
    os.path.join(
        output_dir,
        f"{video_name}_final_motion.mot"
    )
)
print("=" * 60)