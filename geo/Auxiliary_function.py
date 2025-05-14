import re
from Geometric_function import dist, angle, angle_bisector, equal_line,  ortho, online, midpoint,parallel,angle_relation,arc_midpoint, online_extension, online_inside, calc_var_from_dist, is_point_in_triangle, is_acute_triangle, is_point_out_triangle, line_ratio
from openai import OpenAI

calculate_point_function = ['midpoint']
func_information = {
    'dist': 'dist(A,B,value)表示两点AB之间的距离为\{value\}',
    'angle': 'angle(A,B,C,value)表示角ABC的度数为value或者∠ABC=\{value\}°',
    'angle_bisector': '计算角的平分线',
    'equal_line': 'equal_line(A,B,C,D)表示AB等于CD',
    'ortho': '判断两个向量是否正交',
    'online': '判断点是否在直线上',
    'online_inside': '判断点是否在直线上',
    'online_extension': '判断点是否在直线的延长线上',
    'midpoint': '计算线段的中点',
    'parallel': '其中parallel(A,B,C,D)表示AB与CD平行',
    'angle_relation': '计算两个角之间的关系',
    'arc_midpoint': '计算圆弧的中点',
    "is_point_in_triangle": "判断点是否在三角形内",
    "is_acute_triangle": "判断三角形是否为锐角三角形",
    "is_point_out_triangle": "判断点是否在三角形外",
    "line_ratio": "判断线段的比例关系"
}

def LLM_check(text,condition):
    client = OpenAI(
        api_key=" sk-873d65a2fa6945d3801542466346654d",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    cond_key = condition[0]
    if cond_key == "dist" or cond_key == 'online_inside' or cond_key == 'ortho' or cond_key == 'equal_line' or cond_key =='online_extension' or cond_key =='angle' or cond_key =='midpoint' or cond_key =='angle_relation':
        return True
    cond_value = condition[1]
    cond_info = func_information[cond_key]
    params_str = "("
    for index in range(len(cond_value)):
        if index == len(cond_value) - 1:
            params_str += f"{cond_value[index]})"
        else:
            params_str += f"{cond_value[index]}, "
    query = f'题目：{text}，条件：{cond_key}{params_str},其中该条件的意思为{cond_info}，请据此意思判断从题目中是否能推出该条件，并只用"yes"或"no"回答。'
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {
                "role": "system",
                "content": ""
            },
            {"role": "user", "content": query},
        ],
        temperature=0.0,
        stream=False
    )

    # 提取响应中的 yes/no 信息
    condition_satisfied = response.choices[0].message.content.strip().lower()
    if "yes" in condition_satisfied:
        return True
    else:
        return False



def convert_conditions(text,variables,coordinates,conditions_str, radius=None):
    """
    从给定的字符串中解析条件信息，并生成一个列表 conditions。

    参数：
    conditions_str -- 包含条件信息的字符串，每行一个条件

    返回值：
    返回一个列表，其中每个元素是一个元组，包含条件类型（'angle' 或 'dist'）和对应的参数
    """
    conditions = []
    calculate_point_conditions = []
    lines = conditions_str.strip().split('\n')

    for line in lines:
        match = re.match(r"'(\w+)':\s*(\w+)\((.*)\)", line.strip())
        if match:
            condition_type = match.group(1)
            function_name = match.group(2)
            params = [param.strip() for param in re.split(r',\s*(?![^(]*\))', match.group(3))]
            if check_function_format(function_name,params, radius):
                if condition_type in calculate_point_function:
                    calculate_point_conditions.append([function_name,params])
                else:
                    conditions.append([function_name,params])
    for cond in reversed(conditions):
        # check wirh LLM whether the condition is right or not
        condition_right = LLM_check(text,cond)
        if not condition_right:
            conditions.remove(cond)
            print("\n check with LLM, delete condition:\n")
            print(cond)

                
# delete conditions that have already satisfied.
    conditions_excute = []
    for cond in reversed(conditions):
        cond_key = cond[0]
        cond_value = cond[1]
        if cond_key == 'equal_line' and len(cond_value) == 3:
            cond_key = 'dist'
        # check whether the condition is already satisifed or not
        params_str='variables,'
        if cond_key == 'dist' or cond_key == 'angle' or cond_key == 'angle_relation' or cond_key == 'line_ratio':
            for index in range(len(cond_value)):
                if index == len(cond_value) - 1:
                    # params_str += f"{int(cond_value[index])/10}"
                    params_str += f"{cond_value[index]},coordinates"
                else:
                    params_str += f"coordinates['{cond_value[index]}'],"
        else:
            for index in range(len(cond_value)):
                if index == len(cond_value) - 1:
                    # params_str += f"{int(cond_value[index])/10}"
                    params_str += f"coordinates['{cond_value[index]}'],coordinates"
                else:
                    params_str += f"coordinates['{cond_value[index]}'],"

        excute_code=f"{cond_key}({params_str})"

        try:
            # 尝试执行条件代码
            is_satisfied, is_calculate = eval(excute_code)
            if is_calculate:
                if is_satisfied:
                    conditions.remove(cond)
                    print("\n already satiified, delete condition:\n")
                    print(excute_code)
            else:
                conditions_excute.append(excute_code)
        except Exception as e:
            print(excute_code)
            print("不能执行条件代码in convert_conditions")
            conditions=None
            break
    conditions_excute_reverse = []
    for excute_code in reversed(conditions_excute):
        conditions_excute_reverse.append(excute_code)

    #可计算点替换为函数    
    for cond in calculate_point_conditions:
        cond_key = cond[0]
        cond_value = cond[1]
        depend_point = cond_value[0]
        if coordinates[depend_point][0] in variables:
            del variables[coordinates[depend_point][0]]
        if coordinates[depend_point][1] in variables:
            del variables[coordinates[depend_point][1]]
        del coordinates[depend_point]
        dependences=f"calc_{cond_key}(variables,"
        for index in range(1, len(cond_value)):
            dependences+=f"coordinates['{cond_value[index]}'],"
        coordinates[depend_point] = [dependences+'coordinates)']
    print(coordinates)
    print(variables)

    print(calculate_point_conditions)
    print(conditions_excute_reverse)
    return coordinates,variables,calculate_point_conditions,conditions_excute_reverse

"""生成符合对应格式的字典"""
def parse_points_info(points_str):
    """
    从给定的字符串中解析点的坐标信息，并生成一个字典 points_info。

    参数：
    points_str -- 包含点和坐标信息的字符串，每行一个点和对应的坐标

    返回值：
    返回一个字典，其中键是点的名称，值是点的坐标（已知的坐标为元组形式，未知的坐标为字符串）
    """
    points_info = {}
    points_str = points_str.replace(" ", "")
    lines = points_str.strip().split('\n')

    for line in lines:
        match = re.match(r"'(\w)':\(([^,]+),([^,]+)\)", line.strip())
        if match:
            point = match.group(1)
            x, y = match.group(2), match.group(3)
            if x.replace('.', '', 1).isdigit() and y.replace('.', '', 1).isdigit():
                points_info[point] = (float(x), float(y))
            else:
                points_info[point] = f"{x}, {y}"

    return points_info

"""利用对应格式的字典生成变量"""
def convert_coordinates(coordinates, radius=None):
    def parse_value(value):
        # 替换特定的字母
        if value == 'r':
            return radius if radius is not None else 1.0, False
        elif value == '-r':
            return -radius if radius is not None else -1.0, False
        else:
            # 尝试转换为浮点数
            try:
                return float(value), False
            except ValueError:
                return value, True

    converted_coords = {}
    variable_names = {}

    for key, value in coordinates.items():
        if isinstance(value, tuple):
            # 如果已经是元组，直接添加到结果中
            converted_coords[key] = value
        else:
            # 处理字符串类型的坐标
            # 使用逗号分隔字符串并去除空格
            parts = value.split(',')
            # 创建新的坐标元组
            coord_value = []
            for part in parts:
                value, is_string = parse_value(part.strip())
                if is_string:
                    if value not in variable_names.keys():
                        # 如果变量名不在字典中，添加它
                        variable_names[value] = [0, False]
                coord_value.append(value)
            new_value = tuple(coord_value)
            converted_coords[key] = new_value

    return converted_coords, variable_names

"""提取坐标和条件信息"""
def extract_info(text):
    # 使用正则表达式匹配坐标和条件信息
    coord_pattern = re.compile(r'坐标：\s*{([^}]*)}', re.DOTALL)
    cond_pattern = re.compile(r'条件：\s*{([^}]*)}', re.DOTALL)

    coords = coord_pattern.search(text)
    conds = cond_pattern.search(text)

    coord_info = coords.group(1).strip() if coords else ""
    cond_info = conds.group(1).strip() if conds else ""

    return coord_info, cond_info
"""提取条件信息"""
def parse_conditions(conditions_str):
    """
    从给定的字符串中解析条件信息，并生成一个列表 conditions。

    参数：
    conditions_str -- 包含条件信息的字符串，每行一个条件

    返回值：
    返回一个列表，其中每个元素是一个元组，包含条件类型（'angle' 或 'dist'）和对应的参数
    """
    conditions = []
    lines = conditions_str.strip().split('\n')

    for line in lines:
        match = re.match(r"'(\w+)':\s*(\w+)\(([^)]+)\)", line.strip())
        if match:
            condition_type = match.group(1)
            function_name = match.group(2)
            params = match.group(3).split(', ')
            conditions.append((condition_type, function_name, params))

    return conditions


def is_number(s, radius=None):
    try:
        # 尝试将输入转换为浮点数
        return float(s), True
    except ValueError:
        if s == 'r':
            # 如果 s 是 'r'，根据给定的半径返回 1.0 或者 None
            return radius if radius is not None else 1.0, True
        elif s == '-r':
            # 如果 s 是 '-r'，根据给定的半径返回 -1.0 或者 None
            return -radius if radius is not None else -1.0, True
        else:
            # 其他情况，返回原始字符串
            return s, False


def check_function_format(function_name,params, radius=None):
    """
        检查输入的函数名和参数格式是否正确。

        参数:
            function_name (str): 函数的名称，可能是 'angle' 或 'dist'。
            params (list): 与函数相关的参数列表。

        返回:
            bool: 如果参数格式正确且最后一个参数是一个数值，返回 True；否则返回 False。
        """
    if function_name=="angle":
        if len(params)==4:
            value,is_number_value = is_number(params[3])
            params[3]=value
            return is_number_value
        else:
            return False
    elif function_name=="dist":
        if len(params)==3:
            value,is_number_value = is_number(params[2], radius)
            params[2]=value
            return is_number_value
        else:
            return False
    elif function_name == "line_ratio":
        if len(params) == 5:
            value, is_number_value = is_number(params[4])  # 检查倍数因子 k 是否为数字
            params[4] = value
            return is_number_value
        else:
            return False
    elif function_name == "equal_line":
        # 检查 equal_line 是否有 4 个参数
        return len(params) == 4 or len(params) == 3
    # elif function_name == "equal_segment":
    #     # 检查 equal_segment 是否有 3 个参数
    #     return len(params) == 3
    elif function_name == "ortho":
        # 检查 ortho 是否有 4 个参数
        return len(params) == 4
    elif function_name == "online":
        # 检查 online 是否有 3 个参数
        return len(params) == 3
    elif function_name == "online_extension":
        # 检查 online 是否有 3 个参数
        return len(params) == 3
    elif function_name == "online_inside":
        # 检查 online 是否有 3 个参数
        return len(params) == 3
    elif function_name == "midpoint":
        # 检查 midpoint 是否有 3 个参数
        return len(params) == 3
    elif function_name == "angle_bisector":
        # 检查 angle_bisector 是否有 3 个参数
        return len(params) == 5
    elif function_name == "parallel":
        # 检查 parallel 是否有 3 个参数
        return len(params) == 4
    elif function_name == "is_point_in_triangle":
        # 检查 is_point_in_triangle 是否有 4 个参数
        return len(params) == 4
    elif function_name == "is_point_out_triangle":
        # 检查 is_point_in_triangle 是否有 4 个参数
        return len(params) == 4
    elif function_name == "is_acute_triangle":
        # 检查 is_acute_triangle 是否有 3 个参数
        return len(params) == 3
    elif function_name == "angle_relation":
        # 检查 angle_relation 是否有 7 个参数
        if len(params) == 7:
            value, is_number_value = is_number(params[6])  # 检查第七个参数
            params[6] = value
            return is_number_value
        else:
            return False
    elif function_name == "arc_midpoint":
        # 检查 arc_midpoint 是否有 3 个参数
        return len(params) == 3
    # else:
    #     print("格式错误，请停止重新启动")
    #     exit()
    else:
        print(f"{function_name} check_function_format 格式错误，请停止重新启动")
        return False


def check_condition_break(condition_code,coordinates,variables):
    """
    检查给定的条件代码是否有效。

    参数：
    condition_code -- 包含条件代码的字符串

    返回值：
    如果条件代码有效，则返回 True；否则返回 False
    """
    if not condition_code:
        return False
    for excute_code in condition_code:
        try:
            # 尝试执行条件代码
            is_satisfied, is_calculate = eval(excute_code)
            if is_calculate:
                if not is_satisfied:
                    # print(excute_code)
                    return True
        except:
            # 如果执行条件代码时发生异常，则条件代码无效
            # print(excute_code)
            print(f"不能执行条件代码 {excute_code} in check_condition_break")
            return True
    return False


def calc_deduct_var_values(deduct_var, variables):
    # print(variables)
    func_name = variables['depend'][deduct_var]['func_name']
    params = variables['depend'][deduct_var]['params']
    excute_code = f'{func_name}('
    for index in range(len(params)):
        if index == len(params) - 1:
            if isinstance(params[index], str):
                excute_code += f"variables['{params[index]}'][0]" + ')'
            else:
                excute_code += f"{params[index]}" + ')'
        else:
            if isinstance(params[index],str):
                excute_code += f"variables['free']['{params[index]}'][0],"
            else:
                excute_code += f"{params[index]},"

    try:
        result = eval(excute_code)
        return result
    except:
        print(excute_code)
        print("不能执行条件代码 in calc_deduct_var_values")
        return None
