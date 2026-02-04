import numpy as np
from Auxiliary_function import check_condition_break

def extract_and_modify(coordinates, condition_code, variables):

    key_list = list(variables.keys())
    flag = len(key_list)
    
    # 打印初始信息
    print(f"Variables count: {flag}")
    print(f"Keys: {key_list}")
    
    if flag == 0:
        return coordinates, variables, True

    # 搜索参数
    low, up, step = -2, 2, 0.01
    search_values = np.around(np.arange(low, up + step, step), decimals=2)

    def backtrack(index):
        if index == flag:
            cond_break = check_condition_break(condition_code, coordinates, variables)
            return not cond_break

        current_key = key_list[index]
        
        for val in search_values:
            # 赋值
            variables[current_key] = [val, True]
            
            # 剪枝优化
            if not check_condition_break(condition_code, coordinates, variables):
                if backtrack(index + 1):
                    return True  # 找到解，逐层向上返回
            
            # 回溯/重置状态
            variables[current_key][1] = False
            
        return False

    # 执行递归搜索
    if backtrack(0):
        print("\nfound a feasible solution!\n")
        print(variables)
        print(coordinates)
        return coordinates, variables, True
    else:
        print("\ndidn't find a feasible solution!\n")
        return coordinates, variables, False
