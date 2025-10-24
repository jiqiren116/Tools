# 喜马拉雅 解析JSON文件，提取所有的tracks数据，按照播放量降序排序，保存到Excel文件

import json
import pandas as pd
from typing import List, Dict

def parse_json_file(file_path: str) -> List[Dict]:
    """
    解析JSON文件，提取所有的tracks数据
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        包含所有tracks的列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 如果文件是数组形式，遍历每个对象
        if isinstance(data, list):
            all_tracks = []
            for item in data:
                if 'data' in item and 'tracks' in item['data']:
                    all_tracks.extend(item['data']['tracks'])
            return all_tracks
        # 如果文件是单个对象
        elif isinstance(data, dict) and 'data' in data and 'tracks' in data['data']:
            return data['data']['tracks']
        else:
            print("JSON文件格式不符合预期")
            return []
            
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return []

def sort_tracks_by_playcount(tracks: List[Dict]) -> List[Dict]:
    """
    按照播放量对tracks进行降序排序
    
    Args:
        tracks: tracks数据列表
        
    Returns:
        排序后的tracks列表
    """
    return sorted(tracks, key=lambda x: x.get('playCount', 0), reverse=True)

def save_to_excel(tracks: List[Dict], output_file: str = 'sorted_tracks.xlsx'):
    """
    将排序后的tracks数据保存到Excel文件
    
    Args:
        tracks: 排序后的tracks数据
        output_file: 输出Excel文件名
    """
    if not tracks:
        print("没有数据可保存")
        return
    
    try:
        # 选择需要导出的字段
        selected_fields = [
            'index', 'trackId', 'title', 'playCount', 'duration', 
            'createDateFormat', 'albumTitle', 'anchorName'
        ]
        
        # 创建数据框
        data = []
        for track in tracks:
            row = {}
            for field in selected_fields:
                row[field] = track.get(field, '')
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # 设置列名中文显示（可选）
        column_names = {
            'index': '序号',
            'trackId': '音轨ID',
            'title': '标题',
            'playCount': '播放量',
            'duration': '时长(秒)',
            'createDateFormat': '创建时间',
            'albumTitle': '专辑标题',
            'anchorName': '主播名称'
        }
        df = df.rename(columns=column_names)
        
        # 保存到Excel
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"数据已成功保存到 {output_file}")
        print(f"共导出 {len(tracks)} 条记录")
        
    except Exception as e:
        print(f"保存Excel文件时发生错误: {e}")

def main():
    """
    主函数：协调整个处理流程
    """
    # 配置参数
    input_file = r'D:\Cmy\Code\Tools\temp_data\huzuohuyou.json'  # 修改为您的JSON文件路径
    output_file = 'sorted_tracks.xlsx'
    
    print("开始处理JSON文件...")
    
    # 1. 解析JSON文件
    tracks = parse_json_file(input_file)
    
    if not tracks:
        print("未找到任何tracks数据，程序结束")
        return
    
    print(f"成功读取 {len(tracks)} 条tracks数据")
    
    # 2. 按播放量排序
    sorted_tracks = sort_tracks_by_playcount(tracks)
    print("数据排序完成")
    
    # 3. 保存到Excel
    save_to_excel(sorted_tracks, output_file)

def create_sample_json():
    """
    创建示例JSON文件（用于测试）
    """
    sample_data = [
        {
            "ret": 200,
            "data": {
                "currentUid": 195213825,
                "albumId": 12817863,
                "trackTotalCount": 547,
                "sort": 1,
                "tracks": [
                    {
                        "index": 547,
                        "trackId": 923376565,
                        "isPaid": False,
                        "tag": 0,
                        "title": "442 渡海劫波：吴石、蔡孝乾与白色恐怖下的台海谍战",
                        "playCount": 15668,
                        "showLikeBtn": True,
                        "isLike": False,
                        "showShareBtn": True,
                        "showCommentBtn": True,
                        "showForwardBtn": True,
                        "createDateFormat": "2天前",
                        "url": "/sound/923376565",
                        "duration": 4729,
                        "isVideo": False,
                        "isVipFirst": False,
                        "breakSecond": 0,
                        "length": 4729,
                        "albumId": 12817863,
                        "albumTitle": "忽左忽右",
                        "albumCoverPath": "group63/M09/B4/93/wKgMaF2jnNbRhxd-AAPFmyK0BY0816.jpg",
                        "anchorId": 104088857,
                        "anchorName": "JustPod",
                        "ximiVipFreeType": 0,
                        "joinXimi": False
                    },
                    {
                        "index": 546,
                        "trackId": 921983453,
                        "isPaid": True,
                        "tag": 4,
                        "title": "电视大战01｜卫星上天，凤凰落地：默多克与刘长乐的华语媒体大冒险",
                        "playCount": 8392,
                        "showLikeBtn": True,
                        "isLike": False,
                        "showShareBtn": True,
                        "showCommentBtn": True,
                        "showForwardBtn": False,
                        "createDateFormat": "6天前",
                        "url": "/sound/921983453",
                        "duration": 4649,
                        "isVideo": False,
                        "isVipFirst": False,
                        "breakSecond": 0,
                        "length": 4649,
                        "albumId": 12817863,
                        "albumTitle": "忽左忽右",
                        "albumCoverPath": "group63/M09/B4/93/wKgMaF2jnNbRhxd-AAPFmyK0BY0816.jpg",
                        "anchorId": 104088857,
                        "anchorName": "JustPod",
                        "ximiVipFreeType": 0,
                        "joinXimi": False
                    }
                ]
            }
        }
    ]
    
    with open('sample_data.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print("示例文件 sample_data.json 已创建")

if __name__ == "__main__":
    # 如果需要创建示例文件进行测试，取消下面的注释
    # create_sample_json()
    
    main()