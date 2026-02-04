import json
import re
import multiprocessing
import time
import math
import os
from openai import OpenAI
from Auxiliary_function import parse_points_info, convert_coordinates, extract_info, convert_conditions
from Kernel_function import extract_and_modify
from latex_pdf_open import get_latex_code, for_render_code, render_latex_to_pdf

# ================= 配置与初始化 =================
API_CONFIG = {
    "api_key": "YOUR_API_KEY",  # 填入你的 API Key
    "base_url": "YOUR_BASE_URL", # 填入你的 Base URL
    "model": "qwen-plus"
}

client = OpenAI(**API_CONFIG)

# ================= 核心工具函数 =================

def call_llm(system_prompt, user_content, temperature=0.0):
    """通用 LLM 调用接口"""
    try:
        response = client.chat.completions.create(
            model=API_CONFIG["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        return ""

def analyze_geometry_context(text):
    system_prompt = (
        "你是一个几何专家。请分析给出的数学题，并以 JSON 格式输出以下信息：\n"
        "1. type: 图形类型(circle/triangle/quad/mixed)\n"
        "2. radius: 如果涉及圆，提取半径数值；如果不确定但有半径概念，设为 1.0；否则为 null\n"
        "3. suggestions: 针对该图形的坐标设置建议（例如：'设圆心O为(0,0)', '设A为(0,0)'）\n"
        "4. is_circle: 布尔值，是否包含圆\n"
        "只输出 JSON，不要回复其他文字。"
    )
    
    res = call_llm(system_prompt, f"题目内容：{text}")
    try:
        clean_json = re.sub(r'```json\n|\n```', '', res)
        analysis = json.loads(clean_json)
        
        radius = analysis.get('radius')
        # 如果是圆且没提取到具体数值，给定默认基准半径 1.0
        if analysis.get('is_circle') and radius is None:
            radius = 1.0
            
        extra_info = f"类型：{analysis.get('type')}。建议：{analysis.get('suggestions')}"
        return extra_info, radius
    except:
        r_match = re.search(r"半径[为是等于]?\s*([0-9.]+)", text)
        radius = float(r_match.group(1)) if r_match else (5.0 if "圆" in text or "⊙" in text else None)
        return "类型判断失败，请根据常识设置坐标", radius

def calcmidpoint(A, B):
    return ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)

def find_midpoint_letters(text):
    midpoint_pattern = r"点([A-Z])(?:、([A-Z]))?(?:分别是|是).*?中点"
    matches = re.findall(midpoint_pattern, text)
    return [letter for pair in matches for letter in pair if letter]

def run_extract_and_modify(generated_points, condition_code, variables, output_queue):
    try:
        res = extract_and_modify(generated_points, condition_code, variables)
        output_queue.put(res)
    except Exception as e:
        output_queue.put(e)



def process_geometry_task(item, generic_knowledge, output_dir="../output"):
    """
    重构后的通用几何题目处理流程
    """
    text = item['subject']
    print(f"\n--- 正在处理题目 ID: {item['id']} ---")
    

    extra_info, radius = analyze_geometry_context(text)
    print(f"[感知结果] 半径: {radius}, 辅助建议: {extra_info}")

    instruct = (
        "根据数学几何题意和辅助信息，执行以下任务：\n"
        "1. 列出所有点的坐标表示（优先使用已知常数，未知用变量，禁止包含角度标记）。\n"
        "2. 列出所有几何约束条件。\n"
        "输出格式必须严格为：\n"
        "坐标：\n{'A':(x,y)}\n"
        "条件：\n{'c1':'x**2 + y**2 = r**2'}"
    )

    # 获取坐标与条件解析 
    full_prompt = f"{generic_knowledge}\n\n当前题目辅助背景：{extra_info}"
    response_text = call_llm(full_prompt, f"题目:{text}\n任务:{instruct}")
    
    if not response_text: 
        print("LLM 解析失败")
        return
    
    coord_info, cond_info = extract_info(response_text)
    points_info = parse_points_info(coord_info)
    
    # 转换坐标与变量 
    generated_points, variables = convert_coordinates(points_info, radius=radius)
    
    # 转换约束条件
    generated_points, variables, calc_cond, condition_code = convert_conditions(
        text, variables, generated_points, cond_info, radius=radius
    )
    
    if not condition_code:
        print("条件方程生成失败")
        return


    output_queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=run_extract_and_modify, 
        args=(generated_points, condition_code, variables, output_queue)
    )
    process.start()
    process.join(600) 

    if process.is_alive():
        process.terminate()
        print("核心计算引擎求解超时")
        return

    try:
        result = output_queue.get_nowait()
        if isinstance(result, Exception): raise result
        modified_coordinates, extracted_variables, found = result
        
        if found:
            fusion = {}
            for point, coords in modified_coordinates.items():
                if len(coords) < 2: continue
                # 获取变量的第一个解
                v1 = extracted_variables.get(coords[0], [coords[0]])[0] if isinstance(coords[0], str) else coords[0]
                v2 = extracted_variables.get(coords[1], [coords[1]])[0] if isinstance(coords[1], str) else coords[1]
                # 统一缩放因子，适配绘图区域
                fusion[point] = (float(v1) * 2, float(v2) * 2) 

            # 处理中点补全逻辑
            if "中点" in text:
                for mid_p in find_midpoint_letters(text):
                    if mid_p in modified_coordinates:
                        match = re.findall(r"coordinates\['([A-Z])'\]", str(modified_coordinates[mid_p]))
                        if len(match) == 2:
                            fusion[mid_p] = calcmidpoint(fusion[match[0]], fusion[match[1]])

            # 7. 渲染输出
            render_geometry_pdf(text, fusion, f"{output_dir}/{item['id']}.pdf")
        else:
            print("未能找到符合条件的数值解")
            
    except Exception as e:
        print(f"处理过程出错: {e}")

def render_geometry_pdf(text, fusion, output_path):
    system_prompt = (
        "你是一个 LaTeX 绘图专家。根据给定的点坐标绘制几何图形。\n"
        "要求：使用 tikz 宏包，\\coordinate 定义点，\\draw 连线，"
        "\\fill (P) circle (1.5pt) node[anchor=south] {P} 标注点。\n"
        "不要包含任何角度符号（°）。只输出 LaTeX 代码。"
    )
    user_content = f"题目：{text}\n坐标数据：{json.dumps(fusion)}"
    
    latex_raw = call_llm(system_prompt, user_content)
    try:
        clean_code = get_latex_code(latex_raw)
        final_code = for_render_code(clean_code)
        render_latex_to_pdf(final_code, output_path)
        print(f"成功导出 PDF: {output_path}")
    except Exception as e:
        print(f"PDF 渲染阶段失败: {e}")



def main(input_json_path):
    knowledge_file = '../prompt/geometry_knowledge.dat'
    with open(knowledge_file, 'r', encoding='utf-8') as f:
        generic_knowledge = f.read()

    # 加载题目
    if not os.path.exists(input_json_path):
        print(f"错误：找不到文件 {input_json_path}")
        return

    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"开始自动化处理任务，共 {len(data)} 题...")
    for item in data:
        process_geometry_task(item, generic_knowledge)

if __name__ == "__main__":
    main('../json/circle.json')
    # main('../json/triangle.json')
    # main('../json/quadrangle.json')
