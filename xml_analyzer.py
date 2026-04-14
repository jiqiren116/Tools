import os
import glob
import xml.etree.ElementTree as ET

# ========== 配置项 ==========
# 请修改为你的XML文件所在文件夹路径（绝对路径或相对路径均可）
FOLDER_PATH = r"C:\Users\cmy\Desktop\xml"  # Windows示例
# FOLDER_PATH = "/home/user/xml_files"  # Linux/Mac示例

# 输出文件路径（绝对路径或相对路径均可）
OUTPUT_FILE = "analysis_result.txt"
# =============================

def extract_basic_ui_testcases(xml_file: str) -> set:
    """
    从单个XML文件中提取name="basic_ui_testcases"的测试项集合
    :param xml_file: XML文件路径
    :return: 去重后的测试项集合（空集表示提取失败）
    """
    testcases = set()
    try:
        # 解析XML文件
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # 查找所有<variable>节点，筛选name属性匹配的节点
        for variable in root.findall("variable"):
            if variable.get("name") == "basic_ui_testcases":
                # 获取节点文本内容（处理空文本情况）
                node_text = variable.text.strip() if variable.text else ""
                
                # 按逗号分割，清理空白字符，过滤空字符串
                testcases = {
                    item.strip() for item in node_text.split(",")
                    if item.strip()  # 排除空项（如末尾逗号导致的空字符串）
                }
                break
        else:
            # 未找到目标节点
            print(f"⚠️  警告：文件 {os.path.basename(xml_file)} 中未找到 name='basic_ui_testcases' 的节点")
    
    except ET.ParseError as e:
        print(f"❌ 错误：文件 {os.path.basename(xml_file)} 解析失败（XML格式错误）- {str(e)}")
    except Exception as e:
        print(f"❌ 错误：处理文件 {os.path.basename(xml_file)} 时异常 - {str(e)}")
    
    return testcases

def generate_analysis_results(file_testcases: dict) -> str:
    """
    生成分析结果字符串，包含并集、交集和每个文件的特有部分
    """
    result_lines = []
    result_lines.append("=" * 100)
    result_lines.append("📊 XML文件 basic_ui_testcases 分析报告")
    result_lines.append("=" * 100)
    
    # 基础统计信息
    result_lines.append(f"\n[基础统计]")
    result_lines.append(f"📁 分析的XML文件总数：{len(file_testcases)}")
    
    # 计算所有文件的并集
    all_testcases = set().union(*file_testcases.values())
    result_lines.append(f"📈 所有文件不重复测试项总数（并集）：{len(all_testcases)}")
    
    # 计算所有文件的交集
    if file_testcases:
        # 初始化交集为第一个文件的测试项
        common_testcases = next(iter(file_testcases.values())).copy()
        # 依次与其他文件的测试项取交集
        for testcases in list(file_testcases.values())[1:]:
            common_testcases.intersection_update(testcases)
        result_lines.append(f"🔄 所有文件共有的测试项数量（交集）：{len(common_testcases)}")
    else:
        common_testcases = set()
        result_lines.append(f"🔄 所有文件共有的测试项数量（交集）：0")
    
    # 所有不重复测试项列表（并集）
    result_lines.append(f"\n[1. 所有不重复测试项列表（并集）]")
    for idx, item in enumerate(sorted(all_testcases), 1):
        result_lines.append(f"  {idx:2d}. {item}")
    
    # 所有文件共有的测试项列表（交集）
    result_lines.append(f"\n[2. 所有文件共有的测试项列表（交集）]")
    if common_testcases:
        for idx, item in enumerate(sorted(common_testcases), 1):
            result_lines.append(f"  {idx:2d}. {item}")
    else:
        result_lines.append("  ⚠️  没有找到所有文件共有的测试项")
    
    # 每个文件特有的测试项
    result_lines.append(f"\n[3. 每个文件特有的测试项]")
    for filename, testcases in file_testcases.items():
        # 计算特有测试项 = 该文件的测试项 - 所有文件的交集
        unique_testcases = testcases - common_testcases
        result_lines.append(f"\n  📄 {filename}（特有项数量：{len(unique_testcases)}）：")
        if unique_testcases:
            for idx, item in enumerate(sorted(unique_testcases), 1):
                result_lines.append(f"    {idx:2d}. {item}")
        else:
            result_lines.append(f"    ⚠️  该文件没有特有的测试项（所有测试项都在交集中）")
    
    result_lines.append(f"\n✅ 分析完成！")
    
    return "\n".join(result_lines)

def main():
    # 1. 查找文件夹中所有XML文件
    xml_files = glob.glob(os.path.join(FOLDER_PATH, "*.xml"))
    if not xml_files:
        print(f"❌ 错误：在路径 {FOLDER_PATH} 中未找到任何XML文件，请检查路径是否正确")
        return
    
    # 2. 提取每个文件的basic_ui_testcases测试项
    print(f"🔍 正在扫描 {len(xml_files)} 个XML文件...")
    file_testcases = {}
    for xml_file in xml_files:
        filename = os.path.basename(xml_file)
        testcases = extract_basic_ui_testcases(xml_file)
        file_testcases[filename] = testcases
    
    # 过滤掉提取失败的文件（可选）
    file_testcases = {k: v for k, v in file_testcases.items() if v}
    if not file_testcases:
        print(f"❌ 错误：所有XML文件均未成功提取到测试项")
        return
    
    # 3. 生成分析结果（包含并集、交集和特有部分）
    analysis_result = generate_analysis_results(file_testcases)
    
    # 4. 将结果写入文件
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(analysis_result)
        print(f"✅ 分析结果已成功写入文件：{os.path.abspath(OUTPUT_FILE)}")
    except Exception as e:
        print(f"❌ 错误：写入结果文件时异常 - {str(e)}")
    
    # 保留原始的控制台输出函数以便向后兼容
    def print_analysis_results(file_testcases, all_testcases=None, common_testcases=None):
        print(generate_analysis_results(file_testcases))

if __name__ == "__main__":
    main()