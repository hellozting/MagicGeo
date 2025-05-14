import json
import re
import multiprocessing
from openai import OpenAI
from Auxiliary_function import parse_points_info, convert_coordinates, extract_info, convert_conditions
from Kernel_function import extract_and_modify
from latex_pdf_open import get_latex_code, for_render_code, render_latex_to_pdf
import time
import math
def calcmidpoint(A, B):
    mid_x = (A[0] + B[0]) / 2
    mid_y = (A[1] + B[1]) / 2
    return (mid_x, mid_y)

def find_midpoint_letters(text):
    # 匹配格式：点D、E分别是AB、AC的中点；点D是AB中点
    midpoint_pattern = r"点([A-Z])(?:、([A-Z]))?(?:分别是|是).*?中点"

    # 查找所有匹配的中点字母
    matches = re.findall(midpoint_pattern, text)

    # 处理匹配结果
    midpoint_list = [letter for pair in matches for letter in pair if letter]

    return midpoint_list

def run_extract_and_modify(generated_points, condition_code, variables, output_queue):
    try:
        # 调用 extract_and_modify 函数
        modified_coordinates, extracted_variables, found = extract_and_modify(generated_points, condition_code, variables)
        # 将结果放入队列
        output_queue.put((modified_coordinates, extracted_variables, found))
    except Exception as e:
        output_queue.put(e)

def extract_radius_or_diameter(text):
    """从文本中提取半径或直径的值"""
    radius = None

    # 匹配类似“半径为10”或“直径为20”的描述
    radius_match = re.search(r"半径[为是等于]?\s*([0-9]+(\.[0-9]+)?)", text)
    diameter_match = re.search(r"直径[为是等于]?\s*([0-9]+(\.[0-9]+)?)", text)

    if radius_match:
        # 提取半径值
        radius = float(radius_match.group(1))
        print(f"提取到的半径: {radius}")
    elif diameter_match:
        # 提取直径并将其除以2得到半径
        diameter = float(diameter_match.group(1))
        radius = diameter / 2
        print(f"提取到的直径: {diameter}，计算出的半径: {radius}")

    return radius

def any_number_without_degree(text):
    """
    判断文本中是否存在至少一个不带度数符号 (°) 的数值，
    同时去除类似 ∠CAB=2∠EAB 的表达。

    :param text: str, 要检查的文本
    :return: bool, 如果存在至少一个不带°的数值则返回True，否则返回False
    """
    # 去除类似 ∠CAB=2∠EAB 的表达
    text = re.sub(r"∠\w+=\d*∠\w+", "", text)

    # 匹配所有带有°的数值，允许其后面带有空格和 ° 符号
    pattern = r"\d+\s*°"

    # 查找所有数值（不管后面有没有带°）
    all_numbers_pattern = r"\d+"

    # 找到所有带°的数值
    numbers_with_degree = re.findall(pattern, text)

    # 找到所有数值
    all_numbers = re.findall(all_numbers_pattern, text)

    # 如果带°的数值数量和所有数值数量不相等，则存在不带°的数值
    return len(numbers_with_degree) != len(all_numbers)

def generate_coordinates(modified_coordinates, extracted_variables):
    # 创建一个空的字典来存储新的坐标信息
    new_coordinates = {}
    for point, coords in modified_coordinates.items():
        if len(coords) == 1:
            continue
        # 检查坐标是否是数字，还是变量名
        if isinstance(coords, tuple):
            value1 = extracted_variables.get(coords[0], [coords[0]])[0] if isinstance(coords[0], str) else coords[0]
            value2 = extracted_variables.get(coords[1], [coords[1]])[0] if isinstance(coords[1], str) else coords[1]
        else:
            # 直接使用数值坐标
            value1, value2 = coords

        # 将坐标添加到新字典中
        # new_coordinates[point] = (value1, value2)
        new_coordinates[point] = (value1 * 2, value2 * 2)
    return new_coordinates

def extract_diameter_endpoints(problem):
    # 更新正则表达式，确保能够匹配“AB为⊙O的直径”等表述
    diameter_patterns = [
        r"(?:直径|对角线)\s*([A-Z])([A-Z])",  # 匹配 "直径AB" 或 "对角线BD"
        r"([A-Z]+)\s*是\s*⊙O的直径",  # 匹配 "AB是⊙O的直径"
        r"([A-Z])([A-Z])\s*是⊙O的直径",  # 处理 "AB是⊙O的直径" 的变体
        r"([A-Z]+)\s*为\s*⊙O的直径"  # 匹配 "AB为⊙O的直径"
        r"([A-Z]+)\s*为直径"  # 匹配 "AB为直径"
    ]
    endpoints = []
    for pattern in diameter_patterns:
        match = re.search(pattern, problem)
        if match:
            # 根据匹配的分组数量提取端点
            if len(match.groups()) == 2:
                endpoints.append((match.group(1), match.group(2)))  # 直径端点
            elif len(match.groups()) == 1:
                # 处理单个匹配（如 "AB是⊙O的直径"）
                endpoints.append((match.group(1)[0], match.group(1)[1]))
            break  # 找到第一个匹配后退出循环
    return endpoints

def extract_tangent_points(problem):
    # 定义正则表达式模式，匹配 "BC与⊙O相切于点B" 等表述
    tangent_pattern = r"([A-Z]+)\s*与\s*⊙O\s*相切\s*于\s*点\s*([A-Z])"

    match = re.search(tangent_pattern, problem)
    if match:
        # 提取“与”前面的字母和“于”后面的字母
        before_and = match.group(1)  # “与”前面的字母
        after_at = match.group(2)  # “于”后面的字母
        # 删除前面字母的重复部分
        before_and = ''.join([i for i in before_and if i not in after_at])
        # 将结果组合成元组返回
        return (before_and, after_at)
    else:
        # 如果没有匹配，返回空列表
        return []


def circle_main():
    client = OpenAI(
        api_key="",
        base_url="",
    )
    # 读取 JSON 文件
    with open('../circle_75.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    # 读取knowledge
    with open('../prompt/circle_knowledge.dat', 'r', encoding='utf-8') as file:
        circle_prompt = file.read()
    print(circle_prompt)
    convert_prompt = circle_prompt
    # 遍历每个 JSON 对象
    index = -1
    for item in json_data:
        index += 1
        if index <= -1:
            continue
        text = item['subject']
        max_attempts = 1
        attempt = 0
        found = False
        radius = None  # 初始半径为 None，表示还未确定
        # 开始生成几何信息
        while not found and attempt < max_attempts:
            output_file = f"../output/{item['id']}_{attempt}.pdf"
            print(f"题目: {item['id']}:{item['subject']}")
            # 先检查题目是否给出了半径或直径
            radius = extract_radius_or_diameter(text)
            diameter_info=f"半径为{radius}"
            tangent_info = ""
            if radius is None and ("圆" in text or "半径" in text or "直径" in text or "⊙" in text):
                endpoints = extract_diameter_endpoints(text)
                if endpoints:
                    A, B = endpoints[0]
                    diameter_info=f"({A}{B}是直径，设置{A}和{B}的坐标为(r, 0)和(-r, 0)，设置圆心O点坐标为(0,0)。)"
                else:
                    diameter_info=f"(多个点在圆上，将其中一点的坐标设为 (r, 0)，其余点的坐标则通过变量进行表示（不要用极坐标）。避免将两点坐标设置为 (r, 0) 和 (-r, 0)。设置圆心O点坐标为(0,0)。)"
                endpoints = extract_tangent_points(text)  # 假设这个函数返回一个包含两个端点的列表
                if endpoints and len(endpoints) == 2:  # 确保endpoints不为空并且包含两个元素
                    A, B = endpoints  # 这里假设endpoints直接包含两个端点A和B
                    tangent_info = f"({A}不在圆上)"
                else:
                    tangent_info=""
            print(f'diameter_info:{diameter_info}')
            # 如果题目没有给出半径或直径，检查是否可以通过进一步询问获取半径
            if radius is None and ("圆" in text or "半径" in text or "直径" in text or "⊙" in text) and any_number_without_degree(text):
                # 询问是否可以求出半径
                response = client.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {
                            "role": "system",
                            "content": "判断题目是否涉及圆，如果是，请判断是否可以求出圆的半径，并用'yes'或'no'回答。"
                        },
                        {"role": "user", "content": text},
                    ],
                    temperature=0.0,
                    stream=False
                )

                # 提取响应中的 yes/no 信息
                can_find_radius = response.choices[0].message.content.strip().lower()
                print(f"是否可以求出半径: {can_find_radius}")
                if "yes" in can_find_radius:
                    # 第一步: 获取推理过程和半径计算
                    response = client.chat.completions.create(
                        model="qwen-plus",
                        messages=[
                            {
                                "role": "system",
                                "content": "请根据题目进行完整推理，计算圆的半径，并输出完整的推导过程。"
                            },
                            {"role": "user", "content": text},
                        ],
                        temperature=0.0,
                        stream=False
                    )

                    # 输出推理过程，帮助验证计算
                    response_text = response.choices[0].message.content.strip()
                    print(f"推理过程和计算结果:\n{response_text}")

                    # 第二步: 再次请求只返回数值部分
                    response = client.chat.completions.create(
                        model="qwen-plus",
                        messages=[
                            {
                                "role": "system",
                                "content": "请返回上一步计算出的圆的半径值，只回复一个数字，用有理小数表示。"
                            },
                            {"role": "user", "content": response_text},
                        ],
                        temperature=0.0,
                        stream=False
                    )

                    # 提取半径的数值部分
                    radius_text = response.choices[0].message.content.strip()
                    try:
                        radius = float(radius_text)
                        print(f"圆的半径是: {radius}")
                    except ValueError as e:
                        print(f"错误: 无法将响应内容转换为浮点数: {e}")
            instruct = "根据给出的数学几何图的自然语言，\
                        先列出所有用变量表示的坐标，坐标值用变量，no角度表示，再列出所有条件，条件格式如上描述。\
                        输出格式与下列模式匹配，不用加其他语言描述：\
                        坐标：\
                        {\
                        'name':value,\
                        }\
                        条件：\
                        {\
                        'cond_name':cond_value\
                        }"

            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": convert_prompt
                    },
                    {"role": "user", "content": text + diameter_info + tangent_info + instruct},
                ],
                temperature=0.0,
                stream=False
            )

            # 提取和处理响应
            response_text = response.choices[0].message.content
            print("基本信息:\n" + response_text)
            coord_info, cond_info = extract_info(response_text)
            print("\n坐标信息:\n" + coord_info)
            print("\n条件信息:\n" + cond_info)
            # 在解析之前检查 radius 是否有值，如果有，替换坐标中的 r
            points_info = parse_points_info(coord_info)
            generated_points, variables = convert_coordinates(points_info, radius=radius)  # 传递半径
            print("\n解析后的坐标信息和变量:")
            print(generated_points)
            print(variables)

            # 生成条件
            generated_points,variables, calculate_condition,condition_code = convert_conditions(text,variables, generated_points, cond_info, radius=radius)
            if not condition_code:
                print(f"解析条件时发生错误: ")
                attempt += 1
                continue
            print("\n解析条件变量信息:")
            print(condition_code)

            start=time.time()
            # 处理提取和修改的过程，设置超时控制
            output_queue = multiprocessing.Queue()
            process = multiprocessing.Process(target=run_extract_and_modify, args=(generated_points, condition_code, variables, output_queue))
            process.start()

            # 设置超时时间为20秒
            process.join(3600)

            if process.is_alive():
                process.terminate()
                process.join()
                print(f"题目 {item['id']} 超时，跳过该数据。")
                attempt += 1
                break
            try:
                result = output_queue.get_nowait()
                if isinstance(result, Exception):
                    print(f"题目 {item['id']} 执行过程中发生错误：{result}")
                else:
                    end = time.time()
                    print(f"题目 {item['id']} 求解变量信息耗时：{end - start}秒")
                    modified_coordinates, extracted_variables, found = result
                    if found:
                        fusion = {}
                        if not radius:
                            radius = 1
                        radius_info=f"圆的半径是{radius}"
                        print(f"题目 {item['id']} 处理成功！")
                        print("坐标信息：", modified_coordinates)
                        print("变量信息：", extracted_variables)
                        fusion = generate_coordinates(modified_coordinates,extracted_variables)
                        print("题目:",text+diameter_info+tangent_info)
                        print("各点坐标:",fusion)
                        # 生成LaTeX代码并输出PDF
                        print("生成latex的输入:",f'{text},{radius_info},各点坐标：{str(fusion)}')
                        response = client.chat.completions.create(
                            model="qwen-plus",
                            messages=[
                                {"role": "system", "content": "请给出这幅图像的latex code, 注意正确的坐标位置信息已给出。\
                                 不要标出角度以及角度标记,不要标注角度关系。在latex code里请使用‘\\usepackage\\{calc\\}’。\
                                 确保使用正确的坐标位置信息。标注点时要定义坐标点，画点，字母大小稍小。已标注的字母不要重复标注。不需要标注弧。不需要标注角度。只需要连接相关线段。\
                                 如果有角度描述，应把角度的两条边用线段连接起来，比如描述了角ABC的度数，则连接AB和BC。"},
                                {"role": "user", "content": "几何图文本描述：" + f'{text},{radius_info},各点坐标：{str(fusion)}'},
                            ],
                            temperature=0.0,
                            stream=False
                        )
                        latex_code = response.choices[0].message.content
                        try:
                            latex_code = get_latex_code(latex_code)
                            print("提取的latex code:\n" + latex_code)
                            latex_code = for_render_code(latex_code)
                            print("渲染latex code:\n" + latex_code)
                            render_latex_to_pdf(latex_code, output_file)
                        except:
                            print("latex生成图像错误")
                            break
                            attempt += 1

                        break

            except multiprocessing.queues.Empty:
                print(f"题目 {item['id']} 未能找到解决方案，继续尝试...")

            attempt += 1
        if not found:
            print(f"题目 {item['id']} 处理失败。")


def get_triangle_vertices(text):
    # 使用正则表达式匹配"△"后面的三个大写字母
    if "△" in text:
        match = re.search(r'△([A-Z]{3})', text)
        if match:
            return match.group(1)
    else:
        match = re.search(r'三角形([A-Z]{3})', text)
        if match:
            return match.group(1)
    return None

def get_side_lengths(text, vertices):
    # 匹配边长描述语句，例如 "AB=0.3"、"AC=0.4" 等，不匹配角度（"∠"开头）
    side_lengths = {}
    for match in re.finditer(r'\b([A-Z]{2})=([\d.]+)\b(?!°)', text):
        side = match.group(1)
        length = float(match.group(2))
        # 确保边的字母在三角形顶点集合中
        if all(point in vertices for point in side):
            side_lengths[side] = length
    return side_lengths


def triangle_main():
    client = OpenAI(
        api_key="",
        base_url="",
    )
    # 读取 JSON 文件
    with open('../json/triangle.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # 读取knowledge
    with open('../prompt/triangle_knowledge.dat', 'r', encoding='utf-8') as file:
        triangle_prompt = file.read()
    convert_prompt = triangle_prompt

    # 遍历每个 JSON 对象
    index = -1
    for item in json_data:
        index += 1
        if index  <0:
            continue
        text = item['subject']
        max_attempts = 1
        attempt = 0
        found = False
        radius = None  # 初始半径为 None，表示还未确定

        # 开始生成几何信息
        while not found and attempt < max_attempts:
            output_file = f"../output_ting/{item['id']}_{attempt}.pdf"
            print(f"题目: {item['id']}:{item['subject']}")
            vertices_info=""
            if "△" or "三角形" in text:
                vertices = get_triangle_vertices(text)
                A, B, C = vertices[0], vertices[1], vertices[2]
                if any_number_without_degree(text) :
                    if get_side_lengths(text, vertices):
                        side_lengths=get_side_lengths(text, vertices)
                        first_side, first_length = next(iter(side_lengths.items()))
                        if "等边" in text:
                            vertices_info = f"(设置{B}、{C}和{A}的坐标为(0, 0)、({first_length}, 0)、({0.5*first_length}和 {0.5*first_length*math.sqrt(3)})),如果有某点坐标在{B}{C}上，可设置为(i,0).其他点的坐标统一设置为(i，j),(a,b),(m,n)等)"
                        else:
                            first_point = first_side[0]  # 第一个字母
                            second_point = first_side[1]  # 第二个字母
                            length = first_length  # 数值
                            vertices_info = f"(设置{first_point}和{second_point}的坐标为(0, 0)和({first_length},0))。其余点坐标用未知变量表示)。"
                            # vertices_info = f"(设置{first_point}和{second_point}的坐标为(0, 0)和(0,-{first_length}),如果有某点坐标在{first_point}{second_point}上，可设置为(0,i)。其余点的坐标统一设置为(a,b),(m,n)等))"
                    else:
                        vertices_info = f"(设置{B}、{C}和{A}的坐标为(0, 0)、(x, 0)和(y, z),如果有某点坐标在{B}{C}上，可设置为(i,0).)"
                else:
                    if "等边" in text:
                        vertices_info = f"(设置{B}、{C}和{A}的坐标为(0, 0)、(1, 0)和(0.5, 0.866),如果有某点坐标在{B}{C}上，可设置为(i,0))，其他点的坐标统一设置为(i，j),(a,b),(m,n)等)"
                    else:
                        # vertices_info=f"(设置{B}、{C}和{A}的坐标为(0, 0)、(1, 0)和(x,y)),其他点的坐标统一设置为(a,b),(m,n)等)"
                        vertices_info = f"(设置{B}、{C}的坐标分别为(0, 0)、(1, 0)。其余点用两个变量表示。" #如果前面题目里有条件表示“点X在{B}{C}上（注意字母对应）”，该X点坐标可设置为(i,0))，其余字母用变量表示。"
                        # vertices_info = f"(设置{A}、{B}和{C}的坐标为(0, 0)、(1, 0)和(x,y)),如果有某点坐标在{A}{B}上，可设置为(i,0))"
                        # vertices_info = f"(设置{A}、{B}和{C}的坐标为(0, 0)、(1, 0)和(x,y)),其他点的坐标统一设置为(a,b),(m,n)等)"
            print(f"vertice info : {vertices_info}")
            instruct = "根据给出的数学几何图的自然语言，\
                        先列出所有用变量表示的坐标，坐标值用变量，no角度表示，再列出所有条件，条件格式如上描述。\
                        输出格式与下列模式匹配，不用加其他语言描述：\
                        坐标：\
                        {\
                        'name':value,\
                        }\
                        条件：\
                        {\
                        'cond_name':cond_value\
                        }"
            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": convert_prompt
                    },
                    {"role": "user", "content": "\n 题目:" + text + "\n 任务指令及输出格式:" + instruct + "坐标变量信息:" + vertices_info},
                ],
                temperature=0.0,
                stream=False
            )

            # 提取和处理响应
            response_text = response.choices[0].message.content

            print("基本信息:\n" + response_text)
            coord_info, cond_info = extract_info(response_text)
            print("\n坐标信息:\n" + coord_info)
            print("\n条件信息:\n" + cond_info)

            points_info = parse_points_info(coord_info)
            generated_points, variables = convert_coordinates(points_info, radius=radius)  # 传递半径
            print("\n解析后的坐标信息和变量:")
            print(generated_points)
            print(variables)

            # 生成条件
            generated_points,variables, calculate_condition,condition_code = convert_conditions(text,variables, generated_points, cond_info, radius=radius)
            if not condition_code:
                print("condition code is empty!")
            print("\n解析条件变量信息:")
            print(condition_code)

            start=time.time()
            # 处理提取和修改的过程，设置超时控制
            output_queue = multiprocessing.Queue()
            process = multiprocessing.Process(target=run_extract_and_modify, args=(generated_points, condition_code, variables, output_queue))
            process.start()

            # 设置超时时间为20秒
            process.join(3600)

            if process.is_alive():
                process.terminate()
                process.join()
                print(f"题目 {item['id']} 超时，跳过该数据。")
                attempt += 1
                break

            try:
                result = output_queue.get_nowait()
                if isinstance(result, Exception):
                    print(f"题目 {item['id']} 执行过程中发生错误：{result}")
                else:
                    end = time.time()
                    print(f"题目 {item['id']} 求解变量信息耗时：{end - start}秒")
                    modified_coordinates, extracted_variables, found = result
                    if found:
                        fusion = {}
                        if not radius:
                            radius = 1
                        radius_info=f"圆的半径是{radius}"
                        print(f"题目 {item['id']} 处理成功！")
                        print("坐标信息：", modified_coordinates)
                        print("变量信息：", extracted_variables)
                        fusion = generate_coordinates(modified_coordinates,extracted_variables)
                        if "中点" in text:
                            mid_points = find_midpoint_letters(text)
                            for key in mid_points:
                                if key in modified_coordinates:
                                    match = re.findall(r"coordinates\['([A-Z])'\]", modified_coordinates[key][0])
                                    if len(match) == 2:
                                        point1, point2 = fusion[match[0]], fusion[match[1]]
                                        fusion[key] = calcmidpoint(point1, point2)
                        print("题目:",text+vertices_info)
                        print("各点坐标:",fusion)
                        # 生成LaTeX代码并输出PDF
                        print("生成latex的输入:",f'{text},各点坐标：{str(fusion)}')
                        retry_count = 0
                        max_attempts = 5

                        while retry_count < max_attempts:
                            try:
                                response = client.chat.completions.create(
                                    model="qwen-plus",
                                    messages=[
                                        {"role": "system", "content": "请给出这幅图像的latex code, 注意：\
                                         坐标位置已给出，确保使用正确的坐标信息。\
                                         不标注角度、角度标记或角度关系。\
                                         在latex code里请使用‘\\usepackage\\{calc\\}’。\
                                         使用'\coordinate'标注每个坐标点变量\
                                         对给出的每个坐标点进行标注，请确保所有点使用 \fill 命令绘制，并指定 circle (1pt) 作为点的半径。点的标注应紧随 \fill 命令，并使用 node 命令标注点名。\
                                         标注字母的字体大小随图像整体尺寸自动调整。标注位置与点保持适当距离，避免过远或过近影响阅读。\
                                         不需要标注弧。不需要标注角度，不需要标注直角。只需要连接相关线段。\
                                         如果有角度描述，应把角度的两条边用线段连接起来，比如描述了角ABC的度数，则连接AB和BC。"},
                                        {"role": "user",
                                         "content": "几何图文本描述：" + f'{text},各点坐标：{str(fusion)}'},
                                    ],
                                    temperature=0.0,
                                    stream=False
                                )
                                latex_code = response.choices[0].message.content
                                latex_code = get_latex_code(latex_code)
                                print("提取的latex code:\n" + latex_code)
                                latex_code = for_render_code(latex_code)
                                print("渲染latex code:\n" + latex_code)
                                render_latex_to_pdf(latex_code, output_file)
                                break  # 如果成功渲染，退出循环
                            except Exception as e:
                                print(f"第 {retry_count + 1} 次尝试失败: {e}")
                                print("latex生成图像错误")
                                retry_count += 1
                                if retry_count >= max_attempts:
                                    print("达到最大尝试次数，退出程序")
                                    break
            except multiprocessing.queues.Empty:
                print(f"题目 {item['id']} 未能找到解决方案，继续尝试...")
            attempt += 1

        if not found:
            print(f"题目 {item['id']} 处理失败。")




def get_side_length(text, vertices):
    """
    提取与四边形顶点相关的第一个边长。

    参数:
    - text: 包含边长描述的字符串。
    - vertices: 四边形的四个顶点，按顺序给出，例如 ["A", "B", "C", "D"]。

    返回:
    - 一个元组，包含边名和对应边长 (side, length)。
    - 如果没有找到符合条件的边长，返回 None。
    """
    # 构造允许的边集，例如 {"AB", "BC", "CD", "DA"}
    allowed_sides = {vertices[i] + vertices[(i + 1) % len(vertices)] for i in range(len(vertices))}

    for match in re.finditer(r'\b([A-Z]{2})=([\d.]+)\b(?!°)', text):
        side = match.group(1)
        length = float(match.group(2))
        # 如果找到符合条件的边长，立即返回
        if side in allowed_sides:
            return side, length
    return None

def get_diagonal_length(text, vertices):
    """
    提取与四边形顶点相关的第一个对角线长度。

    参数:
    - text: 包含边长描述的字符串。
    - vertices: 四边形的四个顶点，按顺序给出，例如 ["A", "B", "C", "D"]。

    返回:
    - 一个元组，包含对角线名和对应长度 (diagonal, length)。
    - 如果没有找到符合条件的对角线长度，返回 None。
    """
    # 构造对角线集合，例如 {"AC", "BD"}
    diagonals = {vertices[0] + vertices[2], vertices[1] + vertices[3]}

    for match in re.finditer(r'\b([A-Z]{2})=([\d.]+)\b(?!°)', text):
        side = match.group(1)
        length = float(match.group(2))
        # 如果找到符合条件的对角线长度，立即返回
        if side in diagonals:
            return side, length
    return None


def get_quadrilateral_vertices(text):
    # 使用正则表达式匹配"四边形"、"矩形"、"菱形"、"正方形"后面接着的四个大写字母
    match = re.search(r'(四边形|矩形|菱形|正方形)([A-Z]{4})', text)
    if match:
        shape_type = match.group(1)  # 获取四边形类型
        vertices = list(match.group(2))  # 获取四个顶点字母，返回列表
        return shape_type, vertices
    return None

def extract_points(description: str) -> str:
    """
    从几何描述中提取所有点的字母表示。

    参数:
        description (str): 几何描述的字符串。

    返回:
        str: 所有点的字母表示，按字母顺序排列。
    """
    # 匹配单个大写字母，不管它是否被标点或中文包围
    points = re.findall(r'[A-Z]', description)
    if not points:  # 如果没有匹配到点，返回提示
        return "没有找到任何点"
    # 去重并按字母顺序排序
    unique_points = sorted(set(points))
    # 返回结果作为字符串
    return ''.join(unique_points)

def quad_main():
    client = OpenAI(
        api_key="",
        base_url="",
    )
    # 读取 JSON 文件
    with open('../json/quadrangle.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # 读取knowledge


    with open('../prompt/quard_knowledge.dat', 'r', encoding='utf-8') as file:
        quadrangle_prompt = file.read()
    # print(triangle_prompt)


    convert_prompt = quadrangle_prompt

    # 遍历每个 JSON 对象
    index = -1
    for item in json_data:
        index += 1
        if index <= 69:
            continue
        text = item['subject']
        max_attempts = 1
        attempt = 0
        found = False
        radius = None  # 初始半径为 None，表示还未确定



        # 开始生成几何信息
        while not found and attempt < max_attempts:
            output_file = f"../output/{item['id']}_{attempt}.pdf"
            print(f"题目: {item['id']}:{item['subject']}")
            # 先检查题目是否给出了半径或直径
            points=extract_points(text)
            vertices = get_quadrilateral_vertices(text)
            vertices_info=""
            if "四边形" in text :
                A,B,C,D=vertices[1][0],vertices[1][1],vertices[1][2],vertices[1][3]
                if any_number_without_degree(text) :
                    if get_side_length(text, vertices[1]):
                        side_lengths=get_side_length(text, vertices[1])
                        first_side, first_length = side_lengths[0],side_lengths[1]
                        first_point = first_side[0]  # 第一个字母
                        second_point = first_side[1]  # 第二个字母
                        other_vertices = [v for v in [A,B,C,D] if v not in first_side]
                        if "平行" in text:
                            vertices_info = f"(设置{first_point}、{second_point}、{other_vertices[0]}和{other_vertices[1]}的坐标为(0, 0)、({first_length},0))、(x,y)和(z,y),如果有某点坐标在{first_point}{second_point}上，可设置为(i,0)。其余点的坐标统一设置为(a,b),(m,n)等)"
                        else:
                            vertices_info = f"(设置{first_point}、{second_point}、{other_vertices[0]}和{other_vertices[1]}的坐标为(0, 0)、({first_length},0))、(x,y)和(z,v),如果有某点坐标在{first_point}{second_point}上，可设置为(i,0)。其余点的坐标统一设置为(a,b),(m,n)等)"
                    else:
                        if "平行" in text:
                            vertices_info = f"(设定点{A}、{B}、{C}和{D}的坐标分别为(x, y)、(0, 0)、(w, 0)和(z, y)。若某点的坐标位于线段{B}{C}上，则可将其坐标设定为(i, 0)。若某点的坐标位于线段{A}{D}上，则可将其坐标设定为(j, y)。对于其他点，其坐标统一设定为(a, b)、(m, n)等形式。"
                        else:
                            vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(x, y)、(0,0))、(w,0)和(z,v),如果有某点坐标在{B}{C}上，可设置为(i,0)。其余点的坐标统一设置为(a,b),(m,n)等)"
                else:
                    if "平行" in text:
                        vertices_info = f"(题目提供了一组坐标{points}，其中点{A}、{B}、{C}和{D}的坐标分别定义为(x, y)、(0, 0)、(1, 0)和(z, y)。对于位于线段{B}{C}上的任何点，我们可以将其坐标设定为(i, 0)。同样，对于位于线段{A}{D}上的任何点，我们可以将其坐标设定为(j, y)。)"
                    else:
                        vertices_info = f"(设定点{A}、{B}、{C}和{D}的坐标分别为(x, y)、(0, 0)、(1, 0)和(z, v)。如果存在某点的坐标位于线段{B}{C}上，则可以将其坐标设定为(i, 0)。对于其他点，它们的坐标可以统一设定为(a, b)、(m, n)等。)"
            elif "正方形" in text:
                A,B,C,D=vertices[1][0],vertices[1][1],vertices[1][2],vertices[1][3]
                if any_number_without_degree(text) :
                    if get_side_lengths(text, vertices[1]):
                        side_lengths=get_side_lengths(text, vertices[1])
                        side_lengths=next(iter(side_lengths.values()))
                        vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(0, {side_lengths})、(0,0))、({side_lengths},0)和({side_lengths},{side_lengths}),如果有某点坐标在{B}{C}上，可设置为(i,0)。其余点的坐标统一设置为(a,b),(m,n)等)"
                    else:
                        vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(0, x)、(0,0))、(x,0)和(x,x)。其余点的坐标统一设置为(a,b),(m,n)等)"
                else:
                    vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(0, 1)、(0,0))、(1,0)和(1,1),如果有某点坐标在{B}{C}上，可设置为(i,0)。其余点的坐标统一设置为(a,b),(m,n)等)"
            elif "矩形" in text:
                A, B, C, D = vertices[1][0], vertices[1][1], vertices[1][2], vertices[1][3]
                if any_number_without_degree(text):
                    if get_side_length(text, vertices[1]):
                        side_lengths = get_side_length(text, vertices[1])
                        first_side, first_length = side_lengths[0],side_lengths[1]
                        first_point = first_side[0]  # 第一个字母
                        second_point = first_side[1]  # 第二个字母
                        other_vertices = [v for v in [A, B, C, D] if v not in first_side]
                        vertices_info = f"(设置{first_point}、{second_point}、{other_vertices[0]}和{other_vertices[1]}的坐标为(0, 0))、({first_length},0))、(0,y)和({first_length},y),如果有某点坐标在{first_point}{second_point}上，可设置为(i,0)。其余点的坐标统一设置为(a,b),(m,n)等，不考虑矩形边长的平行性和相等性。)"
                    else:
                        vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(0, y)、(0,0))、(x,0)和(x,y),如果有某点坐标在{B}{C}上，可设置为(i,0)。其余点的坐标统一设置为(a,b),(m,n)等，不考虑矩形边长的平行性和相等性。)"
                else:
                    vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(0, y)、(0,0))、(1,0)和(1,y),如果有某点坐标在{B}{C}上，可设置为(i,0)。如果有某点坐标在{A}{D}上，可设置为(x,y)。其余点的坐标统一设置为(a,b),(m,n)等，不考虑矩形边长的平行性和相等性。)"
            elif "菱形" in text:
                A, B, C, D = vertices[1][0], vertices[1][1], vertices[1][2], vertices[1][3]
                if any_number_without_degree(text):
                    if get_diagonal_length(text, vertices[1]):
                        side_lengths = get_diagonal_length(text, vertices[1])
                        first_side, first_length = side_lengths[0],side_lengths[1]
                        first_point = first_side[0]  # 第一个字母
                        second_point = first_side[1]  # 第二个字母
                        other_vertices = [v for v in [A, B, C, D] if v not in first_side]
                        vertices_info = f"(设置{first_point}、{second_point}、{other_vertices[0]}和{other_vertices[1]}的坐标为(0, 0)、({first_length},0)、(x,y)和(x,-y)。如果有某点坐标在{first_point}{second_point}上,可设置为(i,0)。添加条件，'equal_line': equal({first_point}, {other_vertices[0]}, {other_vertices[0]}, {second_point}),'equal_line': equal({first_point}, {other_vertices[0]}, {first_point}, {other_vertices[1]})"
                    else:
                        vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(0, 0)、(z,y)、(x,0)和(z,-y),如果有某点坐标在{A}{C}上，可设置为(i,0)。添加条件，'equal_line': equal({A}, {B}, {B}, {C}),'equal_line': equal({A}, {B}, {A}, {D})"

                else:
                    vertices_info = f"(设置{A}、{B}、{C}和{D}的坐标为(0, 0)、(x,y))、(1,0)和(x,-y),如果有某点坐标在{A}{C}上，可设置为(i,0)。添加条件，'equal_line': equal({A}, {B}, {B}, {C}),'equal_line': equal({A}, {B}, {A}, {D})"
            if "菱形" in text:
                info = ""
            else:
                info=f"\n(特别的，需要添加条件：'not_online':not_online({vertices[1][0]}, {vertices[1][1]}, {vertices[1][2]}),以确保{vertices[1][0]}, {vertices[1][1]}, {vertices[1][2]}不共线)"

            print(f"vertice info : {vertices_info}, info : {info}")


            instruct = "根据给出的数学几何图的自然语言，\
                        先列出所有用变量表示的坐标，坐标值用变量，no角度表示，再列出所有条件，条件格式如上描述。\
                        输出格式与下列模式匹配，不用加其他语言描述：\
                        坐标：\
                        {\
                        'name':value,\
                        }\
                        条件：\
                        {\
                        'cond_name':cond_value\
                        }"

            response = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": convert_prompt
                    },
                    {"role": "user", "content": "\n 题目:" + text + "\n 任务指令及输出格式:" + instruct + "坐标变量信息:" + vertices_info},
                ],
                temperature=0.0,
                stream=False
            )

            # 提取和处理响应
            response_text = response.choices[0].message.content
            print("基本信息:\n" + response_text)
            coord_info, cond_info = extract_info(response_text)
            print("\n坐标信息:\n" + coord_info)
            print("\n条件信息:\n" + cond_info)

            # 在解析之前检查 radius 是否有值，如果有，替换坐标中的 r
            points_info = parse_points_info(coord_info)
            generated_points, variables = convert_coordinates(points_info, radius=radius)  # 传递半径
            print("\n解析后的坐标信息和变量:")
            print(generated_points)
            print(variables)

            # 生成条件
            generated_points,variables, calculate_condition,condition_code = convert_conditions(text,variables, generated_points, cond_info, radius=radius)
            if not condition_code:
                print("condition code is mepty!")
            print("\n解析条件变量信息:")
            print(condition_code)

            start=time.time()
            # 处理提取和修改的过程，设置超时控制
            output_queue = multiprocessing.Queue()
            process = multiprocessing.Process(target=run_extract_and_modify, args=(generated_points, condition_code, variables, output_queue))
            process.start()

            # 设置超时时间为20秒
            process.join(3600)

            if process.is_alive():
                process.terminate()
                process.join()
                print(f"题目 {item['id']} 超时，跳过该数据。")
                attempt += 1
                break

            try:
                result = output_queue.get_nowait()
                if isinstance(result, Exception):
                    print(f"题目 {item['id']} 执行过程中发生错误：{result}")
                else:
                    end = time.time()
                    print(f"题目 {item['id']} 求解变量信息耗时：{end - start}秒")
                    modified_coordinates, extracted_variables, found = result
                    if found:
                        fusion = {}
                        if not radius:
                            radius = 1
                        radius_info=f"圆的半径是{radius}"
                        print(f"题目 {item['id']} 处理成功！")
                        print("坐标信息：", modified_coordinates)
                        print("变量信息：", extracted_variables)
                        fusion = generate_coordinates(modified_coordinates,extracted_variables)
                        print("题目:",text+vertices_info)
                        print("各点坐标:",fusion)
                        # 生成LaTeX代码并输出PDF
                        print("生成latex的输入:",f'{text},各点坐标：{str(fusion)}')
                        response = client.chat.completions.create(
                            model="qwen-plus",
                            messages=[
                                {"role": "system", "content": "请给出这幅图像的latex code, 注意正确的坐标位置信息已给出。\
                                 不要标出角度以及角度标记,不要标注角度关系。在latex code里请使用‘\\usepackage\\{calc\\}’。\
                                 确保使用正确的坐标位置信息。标注点时要定义坐标点，画点，字母标注的位置 above left or above right,字体0.1pt，字母标注位置离实际点距离近一点。不需要标注弧。不需要标注角度，不需要标注直角。只需要连接相关线段。\
                                 如果有角度描述，应把角度的两条边用线段连接起来，比如描述了角ABC的度数，则连接AB和BC。"},
                                {"role": "user", "content": "几何图文本描述：" + f'{text},各点坐标：{str(fusion)}'},
                            ],
                            temperature=0.0,
                            stream=False
                        )
                        latex_code = response.choices[0].message.content
                        try:
                            latex_code = get_latex_code(latex_code)
                            print("提取的latex code:\n" + latex_code)
                            latex_code = for_render_code(latex_code)
                            print("渲染latex code:\n" + latex_code)
                            render_latex_to_pdf(latex_code, output_file)
                        except:
                            print("latex生成图像错误")
                            break
                            attempt += 1
                        break
            except multiprocessing.queues.Empty:
                print(f"题目 {item['id']} 未能找到解决方案，继续尝试...")
            attempt += 1
        if not found:
            print(f"题目 {item['id']} 处理失败。")

if __name__ == "__main__":
    triangle_main()