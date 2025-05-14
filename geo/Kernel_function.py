import numpy as np
from joblib import Parallel, delayed
import multiprocessing
from itertools import product
from Auxiliary_function import check_condition_break, calc_deduct_var_values
from Geometric_function import check_point_different, check_is_calculate
def extract_and_modify(coordinates,condition_code,variables):
    flag=len(variables)
    key_list = list(variables.keys())
    print(flag)
    print(key_list)
    step=0.01
    up=2
    low=-2
    # print("请输入任意内容以继续:")
    # input()
    # print("继续执行")
    if flag == 0:
        return coordinates, variables, True

    

    if flag == 10:
        for value_0 in np.arange(low, up + step, step):
            variables[key_list[0]] = [value_0, True]
            cond_break = check_condition_break(condition_code, coordinates, variables)
            if cond_break:
                continue
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1, True]
                cond_break = check_condition_break(condition_code, coordinates, variables)
                if cond_break:
                    continue
                for value_2 in np.arange(low, up + step, step):
                    variables[key_list[2]] = [value_2, True]
                    cond_break = check_condition_break(condition_code, coordinates, variables)
                    if cond_break:
                        continue
                    for value_3 in np.arange(low, up + step, step):
                        variables[key_list[3]] = [value_3, True]
                        cond_break = check_condition_break(condition_code, coordinates, variables)
                        if cond_break:
                            continue
                        for value_4 in np.arange(low, up + step, step):
                            variables[key_list[4]] = [value_4, True]
                            cond_break = check_condition_break(condition_code, coordinates, variables)
                            if cond_break:
                                continue
                            for value_5 in np.arange(low, up + step, step):
                                variables[key_list[5]] = [value_5, True]
                                cond_break = check_condition_break(condition_code, coordinates, variables)
                                if cond_break:
                                    continue
                                for value_6 in np.arange(low, up + step, step):
                                    variables[key_list[6]] = [value_6, True]
                                    cond_break = check_condition_break(condition_code, coordinates, variables)
                                    if cond_break:
                                        continue
                                    for value_7 in np.arange(low, up + step, step):
                                        variables[key_list[7]] = [value_7, True]
                                        cond_break = check_condition_break(condition_code, coordinates, variables)
                                        if cond_break:
                                            continue
                                        for value_8 in np.arange(low, up + step, step):
                                            variables[key_list[8]] = [value_8, True]
                                            cond_break = check_condition_break(condition_code, coordinates, variables)
                                            if cond_break:
                                                continue
                                            for value_9 in np.arange(low, up + step, step):
                                                variables[key_list[9]] = [value_9, True]
                                                cond_break = check_condition_break(condition_code, coordinates,
                                                                                   variables)
                                                if not cond_break:
                                                    print("\nfound a feasible solution!\n")
                                                    print(variables)
                                                    print(coordinates)
                                                    return coordinates, variables, True
                                            variables[key_list[9]][1] = False
                                        variables[key_list[8]][1] = False
                                    variables[key_list[7]][1] = False
                                variables[key_list[6]][1] = False
                            variables[key_list[5]][1] = False
                        variables[key_list[4]][1] = False
                    variables[key_list[3]][1] = False
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False
                                            


    if flag == 9:
        for value_0 in np.arange(low, up + step, step):
            variables[key_list[0]] = [value_0, True]
            cond_break = check_condition_break(condition_code, coordinates, variables)
            if cond_break:
                continue
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1, True]
                cond_break = check_condition_break(condition_code, coordinates, variables)
                if cond_break:
                    continue
                for value_2 in np.arange(low, up + step, step):
                    variables[key_list[2]] = [value_2, True]
                    cond_break = check_condition_break(condition_code, coordinates, variables)
                    if cond_break:
                        continue
                    for value_3 in np.arange(low, up + step, step):
                        variables[key_list[3]] = [value_3, True]
                        cond_break = check_condition_break(condition_code, coordinates, variables)
                        if cond_break:
                            continue
                        for value_4 in np.arange(low, up + step, step):
                            variables[key_list[4]] = [value_4, True]
                            cond_break = check_condition_break(condition_code, coordinates, variables)
                            if cond_break:
                                continue
                            for value_5 in np.arange(low, up + step, step):
                                variables[key_list[5]] = [value_5, True]
                                cond_break = check_condition_break(condition_code, coordinates, variables)
                                if cond_break:
                                    continue
                                for value_6 in np.arange(low, up + step, step):
                                    variables[key_list[6]] = [value_6, True]
                                    cond_break = check_condition_break(condition_code, coordinates, variables)
                                    if cond_break:
                                        continue
                                    for value_7 in np.arange(low, up + step, step):
                                        variables[key_list[7]] = [value_7, True]
                                        cond_break = check_condition_break(condition_code, coordinates, variables)
                                        if cond_break:
                                            continue
                                        for value_8 in np.arange(low, up + step, step):
                                            variables[key_list[8]] = [value_8, True]
                                            cond_break = check_condition_break(condition_code, coordinates, variables)
                                        
                                            if not cond_break:
                                                print("\nfound a feasible solution!\n")
                                                print(variables)
                                                print(coordinates)
                                                return coordinates, variables, True
                                        variables[key_list[8]][1] = False
                                    variables[key_list[7]][1] = False
                                variables[key_list[6]][1] = False
                            variables[key_list[5]][1] = False
                        variables[key_list[4]][1] = False
                    variables[key_list[3]][1] = False
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False


    if flag == 8:
        for value_0 in np.arange(low, up + step, step):
            variables[key_list[0]] = [value_0, True]
            cond_break = check_condition_break(condition_code, coordinates, variables)
            if cond_break:
                continue
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1, True]
                cond_break = check_condition_break(condition_code, coordinates, variables)
                if cond_break:
                    continue
                for value_2 in np.arange(low, up + step, step):
                    variables[key_list[2]] = [value_2, True]
                    cond_break = check_condition_break(condition_code, coordinates, variables)
                    if cond_break:
                        continue
                    for value_3 in np.arange(low, up + step, step):
                        variables[key_list[3]] = [value_3, True]
                        cond_break = check_condition_break(condition_code, coordinates, variables)
                        if cond_break:
                            continue
                        for value_4 in np.arange(low, up + step, step):
                            variables[key_list[4]] = [value_4, True]
                            cond_break = check_condition_break(condition_code, coordinates, variables)
                            if cond_break:
                                continue
                            for value_5 in np.arange(low, up + step, step):
                                variables[key_list[5]] = [value_5, True]
                                cond_break = check_condition_break(condition_code, coordinates, variables)
                                if cond_break:
                                    continue
                                for value_6 in np.arange(low, up + step, step):
                                    variables[key_list[6]] = [value_6, True]
                                    cond_break = check_condition_break(condition_code, coordinates, variables)
                                    if cond_break:
                                        continue
                                    for value_7 in np.arange(low, up + step, step):
                                        variables[key_list[7]] = [value_7, True]
                                        cond_break = check_condition_break(condition_code, coordinates, variables)
                                        if not cond_break:
                                            print("\nfound a feasible solution!\n")
                                            print(variables)
                                            print(coordinates)
                                            return coordinates, variables, True
                                    variables[key_list[7]][1] = False
                                variables[key_list[6]][1] = False
                            variables[key_list[5]][1] = False
                        variables[key_list[4]][1] = False
                    variables[key_list[3]][1] = False
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False

    
    

    

    if flag == 7:
        for value_0 in np.arange(low, up + step, step):
            # print(value_0)
            variables[key_list[0]] = [value_0, True]
            cond_break = check_condition_break(condition_code, coordinates, variables)
            if cond_break:
                continue
            for value_1 in np.arange(low, up + step, step):
                # print(f'value_1 = {value_1}')
                variables[key_list[1]] = [value_1, True]
                cond_break = check_condition_break(condition_code, coordinates, variables)
                if cond_break:
                    continue
                for value_2 in np.arange(low, up + step, step):
                    # print(f'value_2 = {value_2}')
                    variables[key_list[2]] = [value_2, True]
                    cond_break = check_condition_break(condition_code, coordinates, variables)
                    if cond_break:
                        continue
                    for value_3 in np.arange(low, up + step, step):
                        variables[key_list[3]] = [value_3, True]
                        cond_break = check_condition_break(condition_code, coordinates, variables)
                        if cond_break:
                            continue
                        for value_4 in np.arange(low, up + step, step):
                            variables[key_list[4]] = [value_4, True]
                            cond_break = check_condition_break(condition_code, coordinates, variables)
                            if cond_break:
                                continue
                            for value_5 in np.arange(low, up + step, step):
                                variables[key_list[5]] = [value_5, True]
                                cond_break = check_condition_break(condition_code, coordinates, variables)
                                if cond_break:
                                    continue
                                for value_6 in np.arange(low, up + step, step):
                                    # print(value_6)
                                    variables[key_list[6]] = [value_6, True]
                                    cond_break = check_condition_break(condition_code, coordinates, variables)
                                    if not cond_break:
                                        print("\nfound a feasible solution!\n")
                                        print(variables)
                                        print(coordinates)
                                        return coordinates, variables, True
                                variables[key_list[6]][1] = False
                            variables[key_list[5]][1] = False
                        variables[key_list[4]][1] = False
                    variables[key_list[3]][1] = False
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False



    if flag == 6:
        for value_0 in np.arange(low, up + step, step):
            variables[key_list[0]] = [value_0, True]
            cond_break = check_condition_break(condition_code, coordinates, variables)
            if cond_break:
                continue
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1, True]
                cond_break = check_condition_break(condition_code, coordinates, variables)
                if cond_break:
                    continue
                for value_2 in np.arange(low, up + step, step):
                    variables[key_list[2]] = [value_2, True]
                    cond_break = check_condition_break(condition_code, coordinates, variables)
                    if cond_break:
                        continue
                    for value_3 in np.arange(low, up + step, step):
                        variables[key_list[3]] = [value_3, True]
                        cond_break = check_condition_break(condition_code, coordinates, variables)
                        if cond_break:
                            continue
                        for value_4 in np.arange(low, up + step, step):
                            variables[key_list[4]] = [value_4, True]
                            cond_break = check_condition_break(condition_code, coordinates, variables)
                            if cond_break:
                                continue
                            for value_5 in np.arange(low, up + step, step):
                                variables[key_list[5]] = [value_5, True]
                                cond_break = check_condition_break(condition_code, coordinates, variables)
                                if not cond_break:
                                    print("\nfound a feasible solution!\n")
                                    print(variables)
                                    print(coordinates)
                                    return coordinates, variables, True
                            variables[key_list[5]][1] = False
                        variables[key_list[4]][1] = False
                    variables[key_list[3]][1] = False
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False

    if flag == 5:
        for value_0 in np.arange(low, up + step, step):
            variables[key_list[0]] = [value_0, True]
            cond_break = check_condition_break(condition_code, coordinates, variables)
            if cond_break:
                continue
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1, True]
                cond_break = check_condition_break(condition_code, coordinates, variables)
                if cond_break:
                    continue
                for value_2 in np.arange(low, up + step, step):
                    variables[key_list[2]] = [value_2, True]
                    cond_break = check_condition_break(condition_code, coordinates, variables)
                    if cond_break:
                        continue
                    for value_3 in np.arange(low, up + step, step):
                        variables[key_list[3]] = [value_3, True]
                        cond_break = check_condition_break(condition_code, coordinates, variables)
                        if cond_break:
                            continue
                        for value_4 in np.arange(low, up + step, step):
                            variables[key_list[4]] = [value_4, True]
                            cond_break = check_condition_break(condition_code, coordinates, variables)
                            if not cond_break:
                                print("\nfound a feasible solution!\n")
                                print(variables)
                                print(coordinates)
                                return coordinates, variables, True
                        variables[key_list[4]][1] = False
                    variables[key_list[3]][1] = False
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False

    if flag == 4:
        for value_0 in np.arange(low, up + step, step):
            # print(f"value_0 = {value_0}")
            variables[key_list[0]] = [value_0,True]
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1,True]
                cond_break = check_condition_break(condition_code,coordinates,variables)
                if cond_break:
                    continue
                for value_2 in np.arange(low, up + step, step):
                    variables[key_list[2]] = [value_2,True]
                    for value_3 in np.arange(low, up + step, step):
                        variables[key_list[3]] = [value_3,True]                       
                        cond_break = check_condition_break(condition_code,coordinates,variables)
                        if not cond_break:
                            print("\nfound a feasible solution!\n")
                            print(variables)
                            print(coordinates)
                            return coordinates, variables, True
                    variables[key_list[3]][1] = False
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False
                



    # def generate_combinations(condition_code, coordinates, variables):
    #     for x1 in np.arange(-2, 2.01, 0.01):
    #         for x2 in np.arange(-2, 2.01, 0.01):
    #             for x3 in np.arange(-2, 2.01, 0.01):
    #                 for x4 in np.arange(-2, 2.01, 0.01):
    #                     yield (x1, x2, x3, x4, condition_code, coordinates, variables)

    # def task(x1, x2, x3, x4,condition_code, coordinates, variables, found_solution):
    #     key_list = list(variables.keys())
    #     variables[key_list[0]] = [x1, True]
    #     variables[key_list[1]] = [x2, True]
    #     variables[key_list[2]] = [x3, True]
    #     variables[key_list[3]] = [x4, True]
    #     if check_condition_break(condition_code, coordinates, variables):
    #         return (x1, x2, x3, x4), False
    #     found_solution.value = True
    #     return (x1, x2, x3, x4), True

    # if flag == 4:
    #     manager = multiprocessing.Manager()
    #     found_solution = manager.Value('b', False)
    #     combinations = generate_combinations(condition_code, coordinates, variables)
    #     print("Start")
    #     results = Parallel(n_jobs=10)(delayed(task)(*combination, found_solution) for combination in combinations if not found_solution.value)
    
    #     for result, found in results:
    #         if found:
    #             print(f"Found a solution: {result}")
    #             break

    if flag == 3:
        for value_0 in np.arange(low, up + step, step):
            # print(f"value_0: {value_0}")
            variables[key_list[0]] = [value_0, True]
            # cond_break = check_condition_break(condition_code, coordinates, variables)
            # if cond_break:
            #     continue
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1, True]
                # cond_break = check_condition_break(condition_code, coordinates, variables)
                # if cond_break:
                #     continue
                for value_2 in np.arange(low, up + step, step):
                    # print(f"value_2: {value_2}")
                    variables[key_list[2]] = [value_2, True]
                    cond_break = check_condition_break(condition_code, coordinates, variables)
                    if not cond_break:
                        print("\nfound a feasible solution!\n")
                        print(variables)
                        print(coordinates)
                        return coordinates, variables, True
                variables[key_list[2]][1] = False
            variables[key_list[1]][1] = False

    if flag == 2:
        for value_0 in np.arange(low, up + step, step):
            # print(f"value_0: {value_0}")
            variables[key_list[0]] = [value_0, True]
            for value_1 in np.arange(low, up + step, step):
                variables[key_list[1]] = [value_1, True]
                cond_break = check_condition_break(condition_code, coordinates, variables)
                if not cond_break:
                    print("\nfound a feasible solution!\n")
                    print(variables)
                    print(coordinates)
                    return coordinates, variables, True
            variables[key_list[1]][1] = False
            # variables[key_list[0]][1] = False

    print("\ndidn't found a feasible solution!\n")
    return coordinates, variables, False

