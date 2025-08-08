"""
Compare dictionary structures from multiple JSON files.
"""

import os
import json


def get_dict_structure(d, prefix=""):
    structure = {}
    
    for key, value in d.items():
        current_path = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            nested_structure = get_dict_structure(value, current_path)
            structure.update(nested_structure)
        else:
            structure[current_path] = type(value).__name__
    
    return structure

def compare_dict_structures(*dicts):
    if not dicts:
        return [], []
    
    structures = []
    for i, d in enumerate(dicts):
        if not isinstance(d, dict):
            raise ValueError(f"인수 {i+1}이 딕셔너리가 아닙니다: {type(d)}")
        structures.append(get_dict_structure(d))
    
    all_paths = set()
    for structure in structures:
        all_paths.update(structure.keys())
    
    common_structure = []
    differences = []
    
    for path in sorted(all_paths):
        path_exists_in_all = all(path in structure for structure in structures)
        
        if path_exists_in_all:
            types = [structure[path] for structure in structures]
            if all(t == types[0] for t in types):
                common_structure.append(f"{path}: {types[0]}")
            else:
                type_info = ", ".join([f"dict{i+1}({t})" for i, t in enumerate(types)])
                differences.append(f"{path}: {type_info}")
        else:
            dict_info = []
            for i, structure in enumerate(structures):
                if path in structure:
                    dict_info.append(f"dict{i+1}({structure[path]})")
                else:
                    dict_info.append(f"dict{i+1}(missing)")
            differences.append(f"{path}: {', '.join(dict_info)}")
    
    return common_structure, differences

def print_comparison_result(common_structure, differences):
    print("=== 공통 구조 (모든 dict에서 key와 value 타입이 동일) ===")
    if common_structure:
        for item in common_structure:
            print(f"  {item}")
    else:
        print("  공통 구조가 없습니다.")
    
    print("\n=== 차이점 (key 누락 또는 value 타입 불일치) ===")
    if differences:
        for item in differences:
            print(f"  {item}")
    else:
        print("  차이점이 없습니다.")

if __name__ == "__main__":
    file_list = [f for f in os.listdir('example_datas') if f.startswith('company_ex') and f.endswith('.json')]
    # file_list = [f for f in os.listdir('example_datas') if f.startswith('talent_ex') and f.endswith('.json')]
    data = []
    for fp in file_list:
        with open(os.path.join('example_datas', fp), 'r') as f:
            data.append(json.load(f))

    common, diff = compare_dict_structures(*data)
    print_comparison_result(common, diff)
