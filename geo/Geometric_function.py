import math

def check_is_calculate(variables,point_list,coordinates):

    is_calculate = True
    for i in range(len(point_list)):
        if len(point_list[i]) == 1:
            point_list[i], is_calculate=eval(point_list[i][0])
            if not is_calculate:
                return is_calculate,point_list
        else:
            point = [point_list[i][0], point_list[i][1]]
            if isinstance(point_list[i][0], str):
                is_calculate = variables[point_list[i][0]][1]
                if not is_calculate:
                    return is_calculate,point_list
                point[0] = variables[point_list[i][0]][0]
            if isinstance(point_list[i][1], str):
                is_calculate = variables[point_list[i][1]][1]
                if not is_calculate:
                    return is_calculate,point_list
                point[1] = variables[point_list[i][1]][0]
            point_list[i] = point
    return is_calculate,point_list

def check_point_different(point_list):
    point_num = len(point_list)
    point = point_list[0]
    close_tolerance = 0.1
    for i in range(1, point_num):
        # 检查 AB 和 CD 的端点是否相近
        if (abs(point[0] - point_list[i][0]) < close_tolerance and abs(point[1] - point_list[i][1]) < close_tolerance):
            return False
    if point_num == 2:
        return True
    else:
        return check_point_different(point_list[1:])


def dist(variables,A, B, r,coordinates):
    is_calculate,point_list= check_is_calculate(variables,[A,B],coordinates)
    if is_calculate:
        A=point_list[0]
        B=point_list[1]
        tolerance = 0.01  # 定义误差范围
        # 计算 AB 的平方距离
        distance_squared = (A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2
        # 计算 r 的平方
        r_squared = r ** 2
        # 使用 math.isclose 进行误差范围内的比较
        return math.isclose(distance_squared, r_squared, abs_tol=tolerance), is_calculate
    return False, is_calculate


def angle(variables,B, A, C, expected_angle,coordinates):
    is_calculate, point_list = check_is_calculate(variables,[B, A, C],coordinates)
    min_distance = 0.4
    if is_calculate:
        # print("angle")
        B=point_list[0]
        A=point_list[1]
        C=point_list[2]

        tolerance = 2
        # 计算向量 AB 和 AC 的坐标
        AB = (B[0] - A[0], B[1] - A[1])
        AC = (C[0] - A[0], C[1] - A[1])
        BC = (B[0] - C[0], B[1] - C[1])
        # 计算 AB 和 AC 的长度
        length_AB = math.sqrt(AB[0] ** 2 + AB[1] ** 2)
        if length_AB < min_distance:
            return False, is_calculate
        length_AC = math.sqrt(AC[0] ** 2 + AC[1] ** 2)
        if length_AC < min_distance:
            return False, is_calculate
        length_BC = math.sqrt(BC[0] ** 2 + BC[1] ** 2)
        if length_BC < min_distance:
            return False, is_calculate
        # 计算 AB 和 AC 的点积
        dot_product = AB[0] * AC[0] + AB[1] * AC[1]
        # 计算角度的余弦值
        cos_angle = dot_product / (length_AB * length_AC)
        # 处理极端情况，避免浮点数精度问题导致超出[-1, 1]范围
        cos_angle = max(min(cos_angle, 1.0), -1.0)
        # 计算角度的弧度值
        angle_rad = math.acos(cos_angle)
        # 将弧度转换为角度
        angle_deg = math.degrees(angle_rad)
        # 比较计算出的角度与预期角度
        if abs(angle_deg - expected_angle) <= tolerance:
            return True, is_calculate
        else:
            return False, is_calculate
    return False, is_calculate

def point_to_line_distance(point, line_start, line_end):
    """
    计算点到直线的距离。

    参数:
        point (tuple): 点的坐标 (x, y)。
        line_start (tuple): 直线的起点坐标 (x, y)。
        line_end (tuple): 直线的终点坐标 (x, y)。

    返回:
        float: 点到直线的距离。
    """
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end

    # 直线的标准式系数 Ax + By + C = 0
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2

    # 距离公式
    distance = abs(A * x0 + B * y0 + C) / math.sqrt(A**2 + B**2)
    return distance


def angle_bisector(variables, A, D, C, A_dup, B, coordinates):
    """
    检查线段 AD 是否平分角 CAB。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, D, C, A_dup, B: 点的坐标或变量名。A 和 A_dup 指向同一点。
        tolerance (float): 容差范围，默认为 1e-3。

    返回:
        tuple: 一个布尔值和计算状态。如果 AD 平分角 CAB，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 确保 A 和 A_dup 是同一点
    # assert A == A_dup, "angle_bisector中，A 和 A_dup 必须是同一点"



    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C, D],coordinates)
    if is_calculate:
        A, B, C, D = point_list
        if not check_point_different([A, B, C, D]):
            return False, is_calculate
        tolerance = 0.01

        AB = (B[0] - A[0], B[1] - A[1])
        AD = (D[0] - A[0], D[1] - A[1])
        AC = (C[0] - A[0], C[1] - A[1])

        # 计算 AB 与 BC 的夹角和 DE 与 EF 的夹角
        def calculate_angle(v1, v2):
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            length_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
            length_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            if length_v1 * length_v2 == 0:
                return 0.0
            cos_angle = dot_product / (length_v1 * length_v2)
            cos_angle = max(min(cos_angle, 1.0), -1.0)
            return math.degrees(math.acos(cos_angle))

        angle_BAD = calculate_angle(AB, AD)
        angle_CAD = calculate_angle(AC, AD)
        if angle_BAD < 10 or angle_CAD < 10:
            return False, is_calculate

        # 检查两距离是否相等
        if math.isclose(angle_BAD, angle_CAD, abs_tol=tolerance):
            return True, is_calculate
    return False, is_calculate



def equal_line(variables, A, B, C, D,coordinates):
    """
    检查线段 AB 和 CD 是否等长。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C, D: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果线段 AB 和 CD 等长，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C, D],coordinates)

    if is_calculate:
        # 更新点的坐标
        
        A = point_list[0]
        B = point_list[1]
        C = point_list[2]
        D = point_list[3]
        

        if not check_point_different([A, B]):
            return False, is_calculate
        if not check_point_different([C, D]):
            return False, is_calculate

        tolerance = 0.01  # 定义误差范围


        # 计算 AB 和 CD 的平方距离
        distance_AB_squared = (A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2
        distance_CD_squared = (C[0] - D[0]) ** 2 + (C[1] - D[1]) ** 2
        # tolerance = 0.01 * distance_AB_squared # 根据AB的长度计算误差范围

        # 使用 math.isclose 比较 AB 和 CD 的平方距离是否相等
        return math.isclose(distance_AB_squared, distance_CD_squared, abs_tol=tolerance), is_calculate

    return False, is_calculate



def ortho(variables, A, B, E, F,coordinates):
    """
    检查线段 AB 是否垂直于 EF。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, E, F: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果线段 AB 和 EF 垂直，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, E, F],coordinates)

    if is_calculate:
        # 更新点的坐标
        A = point_list[0]
        B = point_list[1]
        E = point_list[2]
        F = point_list[3]

        tolerance = 0.02  # 定义误差范围
        # 定义直接比较的容差范围
        close_tolerance = 0.01

        # 检查 AB 和 CD 的端点是否相近
        if (abs(A[0] - B[0]) < close_tolerance and abs(A[1] - B[1]) < close_tolerance):
            return False, is_calculate
        if (abs(E[0] - F[0]) < close_tolerance and abs(E[1] - F[1]) < close_tolerance):
            return False, is_calculate

        # 计算向量 AB 和 EF 的坐标
        AB = (B[0] - A[0], B[1] - A[1])
        EF = (F[0] - E[0], F[1] - E[1])

        # 计算向量 AB 和 EF 的点积
        dot_product = AB[0] * EF[0] + AB[1] * EF[1]
        

        # 如果点积接近于 0，则说明 AB 垂直于 EF
        return math.isclose(dot_product, 0, abs_tol=tolerance), is_calculate

    return False, is_calculate


def online(variables, B, E, F,coordinates):
    """
    检查点 B 是否在线段 EF 上。

    参数:
        variables (dict): 包含变量及其状态的字典。
        B, E, F: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果点 B 在线段 EF 上，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [B, E, F],coordinates)

    if is_calculate:
        # 更新点的坐标
        B = point_list[0]
        E = point_list[1]
        F = point_list[2]

        determinant = B[0] * (E[1] - F[1]) + E[0] * (F[1] - B[1])+ F[0] * (B[1] - E[1])
        EB_length_squared = (B[0]-E[0]) ** 2 + (B[1]-E[1]) ** 2

        # 如果行列式的绝对值小于等于 0.0001，则点 B 在线段 EF 上
        tolerance = 0.012  # 定义误差范围
        return abs(determinant)/(EB_length_squared+1e-6) <= tolerance, is_calculate

    return False, is_calculate

def online_extension(variables, B, E, F,coordinates):
    """
    检查点 B 是否在线段 EF的延长线 上。

    参数:
        variables (dict): 包含变量及其状态的字典。
        B, E, F: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果点 B 在线段 EF 上，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [B, E, F],coordinates)
    # print(point_list)

    if is_calculate:
        # 更新点的坐标
        B = point_list[0]
        E = point_list[1]
        F = point_list[2]
        if not check_point_different([B,E,F]):
            return False, is_calculate
        is_online, is_ = online(variables,B,E,F,coordinates)
        
        if is_online:
            # 提取坐标
            x_b, y_b = B
            x_e, y_e = E
            x_f, y_f = F
            
            # 计算 k
            if x_f - x_e != 0:
                k = (x_b - x_e) / (x_f - x_e)
            elif y_f - y_e != 0:
                k = (y_b - y_e) / (y_f - y_e)
            else:
                # B 和 E 是同一个点，这种情况不成立
                return False, is_calculate
            
            # 判断 k 的值
            # print(k)
            if k > 1 or k < 0:
                return True, is_calculate
    return False, is_calculate


def online_inside(variables, B, E, F,coordinates):
    """
    检查点 B 是否在线段 EF的延长线 上。

    参数:
        variables (dict): 包含变量及其状态的字典。
        B, E, F: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果点 B 在线段 EF 上，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [B, E, F],coordinates)
    # print(point_list)

    if is_calculate:
        # 更新点的坐标
        B = point_list[0]
        E = point_list[1]
        F = point_list[2]
        if not check_point_different([B,E,F]):
            return False, is_calculate
        is_online, is_ = online(variables,B,E,F,coordinates)
        
        if is_online:
            # 提取坐标
            x_b, y_b = B
            x_e, y_e = E
            x_f, y_f = F
            
            # 计算 k
            if x_f - x_e != 0:
                k = (x_b - x_e) / (x_f - x_e)
            elif y_f - y_e != 0:
                k = (y_b - y_e) / (y_f - y_e)
            else:
                # B 和 E 是同一个点，这种情况不成立
                return False, is_calculate
            
            # 判断 k 的值
            # print(k)
            if k > 0 and k < 1:
                return True, is_calculate
    return False, is_calculate

def midpoint(variables, A, B, C,coordinates):
    """
    检查点 A 是否是线段 BC 的中点。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果点 A 是 BC 的中点，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C],coordinates)

    if is_calculate:
        # 更新点的坐标
        A = point_list[0]
        B = point_list[1]
        C = point_list[2]

        tolerance = 0.002  # 定义误差范围
        # 定义直接比较的容差范围
        close_tolerance = 0.05

        # 检查A点与BC的端点是否相近
        if (abs(A[0] - B[0]) < close_tolerance and abs(A[1] - B[1]) < close_tolerance):
            return False, is_calculate
        if (abs(A[0] - C[0]) < close_tolerance and abs(A[1] - C[1]) < close_tolerance):
            return False, is_calculate

        # 计算 B 和 C 的中点
        midpoint_BC = [(B[0] + C[0]) / 2, (B[1] + C[1]) / 2]

        # 计算 A 和 BC 中点之间的距离平方
        distance_squared = (A[0] - midpoint_BC[0]) ** 2 + (A[1] - midpoint_BC[1]) ** 2

        # 检查 A 是否等于 BC 的中点
        return math.isclose(distance_squared, 0, abs_tol=tolerance), is_calculate

    return False, is_calculate


def parallel(variables, A, B, C, D,coordinates):
    """
    检查线段 AB 是否平行于线段 CD。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C, D: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果 AB 平行于 CD，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算

    is_calculate, point_list = check_is_calculate(variables, [A, B, C, D],coordinates)

    if is_calculate:
        A = point_list[0]
        B = point_list[1]
        C = point_list[2]
        D = point_list[3]
        if not check_point_different([A, B, C, D]):
            return False, is_calculate
        
        is_online, ignore = online(variables, A,B,C, coordinates)
        if is_online:
            # print('online')
            return False, is_calculate
        def slope(p1, p2):
            """计算两点之间的斜率"""
            if p2[0] == p1[0]:
                return float('inf')  # 斜率为无穷大（垂直线段）
            return (p2[1] - p1[1]) / (p2[0] - p1[0])

        # 计算线段 AB 和 CD 的斜率
        slope_AB = slope(A, B)
        slope_CD = slope(C, D)

        # 定义容差范围
        tolerance = 0.005

        # 使用 math.isclose 比较斜率是否相等
        return math.isclose(slope_AB, slope_CD, abs_tol=tolerance), is_calculate

    return False, is_calculate


def angle_relation(variables, A, B, C, D, E, F, ratio,coordinates):
    """
    判断 ∠ABC 是否等于 ratio 倍的 ∠DEF。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C, D, E, F: 点的坐标或变量名。
        ratio (float): 角度比率，1 表示 ∠ABC = ∠DEF，2 表示 ∠ABC = 2∠DEF，依此类推。

    返回:
        tuple: 一个布尔值和计算状态。如果满足条件，返回 True 和计算状态；否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C, D, E, F],coordinates)
    if is_calculate:
        A = point_list[0]
        B = point_list[1]
        C = point_list[2]
        D = point_list[3]
        E = point_list[4]
        F = point_list[5]
        if not check_point_different([A,B,C]):
            return False, is_calculate
        if not check_point_different([D,E,F]):
            return False, is_calculate

        tolerance = 0.5  # 容差范围

        # 计算向量 AB、BC、DE 和 EF
        BA = (A[0] - B[0], A[1] - B[1])
        BC = (C[0] - B[0], C[1] - B[1])
        ED = (D[0] - E[0], D[1] - E[1])
        EF = (F[0] - E[0], F[1] - E[1])

        # 计算 AB 与 BC 的夹角和 DE 与 EF 的夹角
        def calculate_angle(v1, v2):
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            length_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
            length_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            if length_v1 * length_v2 == 0:
                return 0.0
            cos_angle = dot_product / (length_v1 * length_v2)
            cos_angle = max(min(cos_angle, 1.0), -1.0)
            return math.degrees(math.acos(cos_angle))

        angle_ABC = calculate_angle(BA, BC)
        angle_DEF = calculate_angle(ED, EF)

        # 判断是否满足 ∠ABC = ratio * ∠DEF
        return math.isclose(angle_ABC, ratio * angle_DEF, abs_tol=tolerance), is_calculate

    return False, is_calculate

def arc_midpoint(variables, A, B, C,coordinates):
    """
    检查点 A 是否是弧 BC 的中点。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C: 点的坐标或变量名。

    返回:
        tuple: 如果 A 是弧 BC 的中点，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C],coordinates)

    if is_calculate:
        A = point_list[0]
        B = point_list[1]
        C = point_list[2]

        tolerance = 0.01  # 定义误差范围
        # 定义直接比较的容差范围
        close_tolerance = 0.05

        # 检查A点与BC的端点是否相近
        if (abs(A[0] - B[0]) < close_tolerance and abs(A[1] - B[1]) < close_tolerance):
            return False, is_calculate
        if (abs(A[0] - C[0]) < close_tolerance and abs(A[1] - C[1]) < close_tolerance):
            return False, is_calculate

        # 计算 AB 和 AC 的平方距离
        distance_AB_squared = (A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2
        distance_AC_squared = (A[0] - C[0]) ** 2 + (A[1] - C[1]) ** 2

        # 判断 A 是否等于 BC 的中点
        return math.isclose(distance_AB_squared, distance_AC_squared, abs_tol=tolerance), is_calculate

    return False, is_calculate


def calc_midpoint(variables, A, B, coordinates):
    """
    检查点 A 是否是线段 BC 的中点。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果点 A 是 BC 的中点，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B], coordinates)

    if is_calculate:
        # 更新点的坐标
        A = point_list[0]
        B = point_list[1]
        mid_x = (A[0] + B[0]) / 2
        mid_y = (A[1] + B[1]) / 2
        return (mid_x, mid_y), is_calculate
    return None, is_calculate


def calc_var_from_dist(a,b,c,dist_val):
    # print(f'a: {a}, b: {b}, c: {c}, dist_val:{dist_val}')
    one_axis_diff_square = dist_val**2 - (a-b)**2
    if one_axis_diff_square < 0:
        return None
    # print(one_axis_diff_square)
    one_axis_diff = math.sqrt(one_axis_diff_square)
    # print(one_axis_diff)
    result = [one_axis_diff-c, c-one_axis_diff]
    # print(result)
    return result


def is_point_in_triangle(variables, A, B, C, P, coordinates):
    """
    优化判断点 P 是否在三角形 ABC 内部的函数，使用向量叉积法。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C, P: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果 P 在三角形 ABC 内部，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C, P], coordinates)

    if is_calculate:
        A, B, C, P = point_list
        # 定义向量叉积计算函数
        def cross_product_sign(O, X, Y):
            # 计算向量叉积并返回其符号
            return (X[0] - O[0]) * (Y[1] - O[1]) - (X[1] - O[1]) * (Y[0] - O[0])

        # 计算三组向量叉积的符号
        cross1 = cross_product_sign(A, B, P)
        cross2 = cross_product_sign(B, C, P)
        cross3 = cross_product_sign(C, A, P)

        # 检查所有叉积的符号是否一致（包括零）
        is_inside = (cross1 > 0 and cross2 > 0 and cross3 > 0) or (cross1 < 0 and cross2 < 0 and cross3 < 0)

        return is_inside, is_calculate

    return False, is_calculate


def line_ratio(variables, A, B, F, G, k, coordinates):
    """
    检查线段 FG 是否是 AB 的 k 倍。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, F, G: 点的坐标或变量名。
        k: 倍数因子，表示 FG 应该是 AB 的 k 倍。

    返回:
        tuple: 一个布尔值和计算状态。如果线段 FG 是 AB 的 k 倍，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, F, G], coordinates)

    if is_calculate:
        # 更新点的坐标
        A, B, F, G = point_list
        tolerance = 0.01  # 定义误差范围

        # 计算 AB 和 FG 的平方距离
        distance_AB_squared = (A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2
        distance_FG_squared = (F[0] - G[0]) ** 2 + (F[1] - G[1]) ** 2

        # 计算 FG 是否是 AB 的 k 倍，考虑平方距离的比例关系
        expected_FG_squared = distance_AB_squared * (k ** 2)

        # 使用 math.isclose 比较距离的平方是否符合倍数关系
        return math.isclose(distance_FG_squared, expected_FG_squared, abs_tol=tolerance), is_calculate

    return False, is_calculate


def is_point_out_triangle(variables, A, B, C, P, coordinates):
    """
    优化判断点 P 是否在三角形 ABC 内部的函数，使用向量叉积法。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C, P: 点的坐标或变量名。

    返回:
        tuple: 一个布尔值和计算状态。如果 P 在三角形 ABC 内部，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C, P], coordinates)

    if is_calculate:
        A, B, C, P = point_list
        # 定义向量叉积计算函数
        def cross_product_sign(O, X, Y):
            # 计算向量叉积并返回其符号
            return (X[0] - O[0]) * (Y[1] - O[1]) - (X[1] - O[1]) * (Y[0] - O[0])

        # 计算三组向量叉积的符号
        cross1 = cross_product_sign(A, B, P)
        cross2 = cross_product_sign(B, C, P)
        cross3 = cross_product_sign(C, A, P)

        # 检查所有叉积的符号是否一致（包括零）
        is_inside = (cross1 > 0 and cross2 > 0 and cross3 > 0) or (cross1 < 0 and cross2 < 0 and cross3 < 0)

        return  not is_inside, is_calculate

    return False, is_calculate

def is_acute_triangle(variables,A,B,C,coordinates):
    """
    判断三角形 ABC 是否为锐角三角形的函数。

    参数:
        variables (dict): 包含变量及其状态的字典。
        A, B, C: 三角形的三个顶点。

    返回:
        tuple: 一个布尔值和计算状态。如果三角形 ABC 是锐角三角形，返回 True 和计算状态；
               否则返回 False 和计算状态。
    """
    # 检查所有点是否可以进行计算
    is_calculate, point_list = check_is_calculate(variables, [A, B, C], coordinates)

    if is_calculate: 
        A, B, C = point_list
        # 计算三角形的三条边长
        def distance_square(A, B):
            return (A[0] - B[0])**2 + (A[1] - B[1])**2
        a = distance_square(A, B)
        b = distance_square(B, C)
        c = distance_square(C, A)

        # 判断是否为锐角三角形
        is_acute = a + b > c and b + c > a and c + a > b

        return is_acute, is_calculate

    return False, is_calculate