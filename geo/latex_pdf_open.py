import tkinter as tk
from tkinter import ttk
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pgf import FigureCanvasPgf
matplotlib.backend_bases.register_backend('pdf', FigureCanvasPgf)
import os

def get_latex_code(user_input):
    latex_code = user_input
    start_index = latex_code.find("\\documentclass")
    end_index = latex_code.find("\\end{document}") + len('\\end{document}')
    latex_code = latex_code[start_index:end_index]
    return latex_code


def for_render_code(latex_code):
    # Ensure \usepackage{tikz} is included
    if "\\usepackage{tikz}" not in latex_code:
        latex_code = "\\usepackage{tikz}\n" + latex_code

    # Ensure \usetikzlibrary{calc} is included
    if "\\usetikzlibrary{calc}" not in latex_code:
        latex_code = latex_code.replace("\\usepackage{tikz}", "\\usepackage{tikz}\n\\usetikzlibrary{calc}")

    start_index = latex_code.find("\\usepackage{tikz}")
    end_index = latex_code.find("\\end{document}") + len('\\end{document}')
    latex_code = latex_code[start_index:end_index]

    return latex_code


def render_latex_to_pdf(latex_code, output_file):
    base_name, ext = os.path.splitext(output_file)
    new_output_file = base_name+'.txt'
    with open(new_output_file, 'w') as file:
        file.write(latex_code)
    plt.rc('text', usetex=False)
    plt.rc('pgf', rcfonts=False, preamble=latex_code)


    fig, ax = plt.subplots(figsize=(4, 4))  # Adjust the size as needed
    ax.axis('off')  # Hide axes
    fig.savefig(output_file)
    plt.close(fig)
    print(f"已存入文件{output_file}")


def show_pdf(file_path):
    # 将PDF转换为图像
    images = convert_from_path(file_path)

    root = tk.Tk()
    root.title("PDF Viewer")

    for image in images:
        # 获取图像的原始尺寸
        width, height = image.size

        # 创建一个与图像尺寸相匹配的画布
        canvas = tk.Canvas(root, width=width, height=height)
        canvas.pack()

        # 将图像调整为画布大小
        photo = ImageTk.PhotoImage(image)

        # 在画布上创建图像
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image = photo  # 保持对图像的引用，防止被垃圾回收

        # 更新画布以显示图像
        canvas.update()
    root.mainloop()





