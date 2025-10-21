# 查找缺失msn的脚本
import pandas as pd
import os

def find_missing_msn(excel_path, json_folder):
    try:
        # 1. 处理Excel中的msn
        print("正在读取Excel文件...")
        df = pd.read_excel(excel_path)
        
        if 'msn' not in df.columns:
            print("错误：Excel文件中未找到名为'msn'的列")
            return
        
        # 清洗msn：去空值、去空格、转大写
        df['msn_clean'] = df['msn'].dropna().astype(str).str.strip().str.upper()
        total_msn_raw = len(df['msn_clean'].dropna())  # 原始数量（去空值）
        msn_excel = df['msn_clean'].dropna().unique()  # 去重后
        total_msn_unique = len(msn_excel)
        excel_set = set(msn_excel)
        print(f"Excel中原始msn数量（去空值）：{total_msn_raw}")
        print(f"Excel中去重后msn数量：{total_msn_unique}")
        
        # 2. 处理JSON文件中的msn
        print("\n正在分析JSON文件夹...")
        if not os.path.isdir(json_folder):
            print(f"错误：JSON文件夹路径不存在 - {json_folder}")
            return
        
        json_msns = set()
        invalid_files = []
        for filename in os.listdir(json_folder):
            if filename.endswith('.json'):
                if '_' in filename:
                    msn = filename.split('_')[0].strip().upper()
                    json_msns.add(msn)
                else:
                    invalid_files.append(filename)
        
        total_json_unique = len(json_msns)
        json_set = json_msns
        print(f"JSON中去重后msn数量：{total_json_unique}")
        if invalid_files:
            print(f"警告：{len(invalid_files)}个JSON文件格式异常（无下划线），已忽略")
        
        # 3. 核心计算：共有、缺失、JSON独有
        common_msn = excel_set & json_set  # 两者共有的msn
        missing_msn = excel_set - json_set  # Excel有而JSON没有（缺失）
        json_extra_msn = json_set - excel_set  # JSON有而Excel没有（额外）
        
        # 4. 输出详细结果
        print("\n===== 详细对比结果 =====")
        print(f"Excel去重后总数：{total_msn_unique}")
        print(f"JSON去重后总数：{total_json_unique}")
        print(f"两者共有的msn数量：{len(common_msn)}")
        print(f"Excel独有的msn数量（缺失）：{len(missing_msn)}")
        print(f"JSON独有的msn数量（额外）：{len(json_extra_msn)}")
        
        # 逻辑验证
        print(f"\n逻辑验证：")
        print(f"Excel独有（{len(missing_msn)}） + 共有（{len(common_msn)}） = {len(missing_msn)+len(common_msn)}（应等于Excel总数{total_msn_unique}）")
        print(f"JSON独有（{len(json_extra_msn)}） + 共有（{len(common_msn)}） = {len(json_extra_msn)+len(common_msn)}（应等于JSON总数{total_json_unique}）")
        
        # 输出缺失的msn列表（仅一次）
        if missing_msn:
            print("\n【缺失的msn】（Excel有，JSON没有）：")
            for idx, msn in enumerate(sorted(missing_msn), 1):
                print(f"{idx}. {msn}")
        
        # 输出JSON独有的msn列表（仅一次）
        if json_extra_msn:
            print("\n【JSON独有的msn】（JSON有，Excel没有）：")
            for idx, msn in enumerate(sorted(json_extra_msn), 1):
                print(f"{idx}. {msn}")
        
    except Exception as e:
        print(f"处理过程中发生错误：{str(e)}")

if __name__ == "__main__":
    # 替换为你的实际路径
    EXCEL_FILE_PATH = r"D:\Users\cmy\Documents\WXWork\1688856889516001\Cache\File\2025-10\KIOSK-4500085111-2000 PCS.xls"  # 例如："C:/data/msn_list.xlsx"
    JSON_FOLDER_PATH = r"C:\Users\cmy\Desktop\251015\251015"     # 例如："C:/data/json_files"
    find_missing_msn(EXCEL_FILE_PATH, JSON_FOLDER_PATH)