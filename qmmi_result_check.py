# 脚本功能说明：
# ADB 检测：首先检查 ADB 是否可用，确保环境正常
# 获取 Root 权限：自动执行adb root命令，确保有足够权限访问 XML 文件
# 拉取 XML 文件：将设备中的ui_default_res.xml文件拉取到本地临时文件
# 解析 XML：提取所有TestCase的name和result属性
# 获取属性值：对每个测试项执行adb shell getprop命令，获取对应属性值
# 结果比对：将 XML 中的结果与 getprop 获取的结果进行比对，并清晰展示

import subprocess
import xml.etree.ElementTree as ET
import os

def check_adb_available():
    """检查ADB是否可用"""
    try:
        # 执行adb version命令检查是否存在
        result = subprocess.run(
            ['adb', 'version'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def run_adb_root():
    """执行adb root命令获取root权限"""
    try:
        result = subprocess.run(
            ['adb', 'root'],
            capture_output=True,
            text=True,
            check=True,
            timeout=15
        )
        print("✅ 成功获取ADB root权限")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ADB root执行失败: {e.stderr.strip()}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ ADB root执行超时")
        return False

def pull_xml_file(local_path):
    """从设备拉取XML文件到本地"""
    remote_path = '/data/user/0/com.qualcomm.qti.qmmi/files/ui_default_res.xml'
    try:
        result = subprocess.run(
            ['adb', 'pull', remote_path, local_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        print(f"✅ 成功拉取XML文件到: {local_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 拉取XML文件失败: {e.stderr.strip()}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ 拉取XML文件超时")
        return False

def parse_test_cases(xml_path):
    """解析XML文件中的TestCase信息"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        test_cases = []
        
        for test_case in root.findall('TestCase'):
            name = test_case.get('name')
            result = test_case.get('result')
            
            if name and result in ['pass', 'fail']:
                test_cases.append({
                    'name': name,
                    'xml_result': result
                })
            else:
                print(f"⚠️ 跳过无效的TestCase: {test_case.attrib}")
        
        return test_cases
    except ET.ParseError as e:
        print(f"❌ XML解析错误: {str(e)}")
        return None
    except FileNotFoundError:
        print(f"❌ XML文件不存在: {xml_path}")
        return None

# 修改 get_prop_result 函数，返回原始值而不是转换后的文本
def get_prop_result(test_name):
    """通过ADB获取指定测试项的属性值"""
    prop_name = f'persist.sys.mmiresult_{test_name}'
    try:
        result = subprocess.run(
            ['adb', 'shell', f'getprop {prop_name}'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        value = result.stdout.strip()
        return value  # 直接返回原始值，不进行转换
    except subprocess.CalledProcessError as e:
        print(f"⚠️ 获取{prop_name}失败: {e.stderr.strip()}")
        return "获取失败"  # 返回具体的错误状态
    except subprocess.TimeoutExpired:
        print(f"⚠️ 获取{prop_name}超时")
        return "超时"

# 修改 compare_results 函数中的比对逻辑
def compare_results(test_cases):
    """比对XML结果和getprop结果"""
    if not test_cases:
        print("❌ 没有可比对的测试用例数据")
        return
    
    print("\n" + "="*60)
    print(f"{'测试项名称':<20} | {'XML结果':<10} | {'getprop结果':<10} | {'比对结果'}")
    print("-"*60)
    
    # 添加统计计数器
    total_count = len(test_cases)
    pass_count = 0
    fail_count = 0
    match_count = 0
    mismatch_count = 0
    cannot_compare_count = 0
    
    for case in test_cases:
        name = case['name']
        xml_res = case['xml_result']
        prop_res = get_prop_result(name)
        
        # 更新XML结果统计
        if xml_res == 'pass':
            pass_count += 1
        else:
            fail_count += 1
        
        # 调整比对逻辑：如果prop_res是'1'或'pass'则视为pass，如果是'-1'或'fail'则视为fail
        # 这样可以兼容原始值和转换值
        xml_value = 1 if xml_res == 'pass' else -1
        prop_value = 1 if prop_res == '1' or prop_res == 'pass' else (-1 if prop_res == '-1' or prop_res == 'fail' else None)
        
        if prop_value is None:
            match = "无法比对"
            status = "⚠️"
            cannot_compare_count += 1
        else:
            match = "一致" if xml_value == prop_value else "不一致"
            status = "✅" if match == "一致" else "❌"
            if match == "一致":
                match_count += 1
            else:
                mismatch_count += 1
        
        print(f"{name:<20} | {xml_res:<10} | {prop_res:<10} | {status} {match}")
    
    print("="*60 + "\n")
    
    # 输出统计信息
    print(f"📊 统计结果: 测试项总数 {total_count} 项, 通过 {pass_count} 项, 失败 {fail_count} 项, 比对结果一致 {match_count} 项, 比对结果不一致 {mismatch_count} 项, 无法比对 {cannot_compare_count} 项")


def main():
    # 检查ADB可用性
    if not check_adb_available():
        print("❌ ADB不可用，请确保ADB已正确安装并添加到环境变量")
        return
    
    # 获取root权限
    if not run_adb_root():
        print("⚠️ 继续尝试操作，但可能因权限问题导致失败")
    
    # 拉取XML文件到本地临时文件
    local_xml = "temp_qmmi_result.xml"
    if not pull_xml_file(local_xml):
        return
    
    # 解析XML获取测试用例
    test_cases = parse_test_cases(local_xml)
    if not test_cases:
        # 清理临时文件
        if os.path.exists(local_xml):
            os.remove(local_xml)
        return
    
    # 比对结果
    compare_results(test_cases)
    
    # 清理临时文件
    if os.path.exists(local_xml):
        os.remove(local_xml)
        # print(f"✅ 已清理临时文件: {local_xml}")

if __name__ == "__main__":
    main()