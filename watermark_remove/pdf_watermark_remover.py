# 创建虚拟环境 python -m venv venv
# 激活虚拟环境 .\venv\Scripts\activate
# 安装依赖 pip install Pillow PyMuPDF opencv-python scikit-image matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple

import fitz  # PyMuPDF
import cv2
import numpy as np
import io
from PIL import Image
import os
from skimage.metrics import structural_similarity as ssim

def extract_images_from_pdf(pdf_path):
    """从PDF文件中提取所有图片"""
    doc = fitz.open(pdf_path)
    images_info = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        # 遍历页面上的所有图片
        for image_index, img in enumerate(image_list, start=1):
            # 获取图片的XREF
            xref = img[0]
            
            # 提取图片
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # 将图片转换为OpenCV格式
            image = Image.open(io.BytesIO(image_bytes))
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # 过滤掉太小的图片（小于8x8像素）
            if image_cv.shape[0] < 8 or image_cv.shape[1] < 8:
                # print(f"忽略小图片: 第{page_num+1}页，尺寸: {image_cv.shape[1]}x{image_cv.shape[0]}")
                continue
            
            # 保存图片信息
            images_info.append({
                "page": page_num,
                "xref": xref,
                "image": image_cv,
                "ext": image_ext,
                "img_info": img
            })
    
    doc.close()
    return images_info

def compare_images(image1, image2):
    """计算两张图片的相似度，返回SSIM分数"""
    # 确保两张图片尺寸相同
    if image1.shape != image2.shape:
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
    
    # 转换为灰度图
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    
    # 使用SSIM计算相似度
    score = ssim(gray1, gray2)
    return score

def remove_watermark_from_pdf(pdf_path, watermark_image_path, similarity_threshold=0.99):
    """从PDF中移除指定的水印图片"""
    # 加载水印参考图片
    watermark_image = cv2.imread(watermark_image_path)
    if watermark_image is None:
        print(f"错误: 无法加载水印参考图片 {watermark_image_path}")
        return False
    
    # 提取PDF中的所有图片
    print(f"正在从 {pdf_path} 中提取图片...")
    images_info = extract_images_from_pdf(pdf_path)
    print(f"在PDF中找到了 {len(images_info)} 张图片")
    
    # 找出所有可能的水印图片
    watermark_images = []
    for i, img_info in enumerate(images_info):
        # print(f"正在比较图片 {i+1}/{len(images_info)}...")
        score = compare_images(img_info["image"], watermark_image)
        # print(f"相似度分数: {score:.4f}")
        
        if score > similarity_threshold:
            print(f"✅ 检测到水印图片!  相似度: {score:.4f}")
            watermark_images.append(img_info)
    
    # 如果没有找到水印，返回
    if not watermark_images:
        print("未检测到水印图片")
        return True
    
    print(f"找到 {len(watermark_images)} 个水印图片，准备移除...")
    
    # 创建用于保存删除图片的文件夹
    # removed_images_folder = os.path.splitext(pdf_path)[0] + "_removed_images"
    # os.makedirs(removed_images_folder, exist_ok=True)
    
    # 移除水印图片
    doc = fitz.open(pdf_path)
    
    # 我们需要从后向前移除，以避免索引变化
    watermark_images.sort(key=lambda x: (x["page"], x["xref"]), reverse=True)
    
    for img_info in watermark_images:
        page = doc[img_info["page"]]
        xref = img_info["xref"]
        
        # 保存即将删除的图片
        # image_cv = img_info["image"]
        # image_ext = img_info["ext"]
        # image_name = f"page{img_info['page'] + 1}_xref{xref}.{image_ext}"
        # image_path = os.path.join(removed_images_folder, image_name)
        # cv2.imwrite(image_path, image_cv)
        # print(f"已保存可能的水印图片到 {image_path}")
        
        # 从页面中删除图片
        page.delete_image(xref)
        # print(f"已从第 {img_info['page']+1} 页移除水印图片")
    
    # 保存修改后的PDF
    temp_path = pdf_path + ".temp"
    doc.save(temp_path)
    doc.close()
    
    # 替换原文件
    os.replace(temp_path, pdf_path)
    print(f"PDF已更新，所有水印图片已移除")
    
    return True

def process_folder(folder_path, watermark_image_path, similarity_threshold=0.99, log_file="processing_log.txt"):
    """递归处理文件夹中的所有PDF文件，并记录处理结果到日志文件"""
    total_count = 0
    success_count = 0
    fail_count = 0
    with open(log_file, "w", encoding="utf-8") as log:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    total_count += 1
                    pdf_path = os.path.join(root, file)
                    log.write(f"正在处理文件: {pdf_path}\n")
                    log.flush()  # 手动刷新缓冲区
                    try:
                        success = remove_watermark_from_pdf(pdf_path, watermark_image_path, similarity_threshold)
                        if success:
                            success_count += 1
                        else:
                            fail_count += 1
                        result = "成功" if success else "失败"
                        log.write(f"处理结果: {result}\n")
                        log.flush()  # 手动刷新缓冲区
                    except Exception as e:
                        fail_count += 1
                        log.write(f"处理出错: {str(e)}\n")
                        log.flush()  # 手动刷新缓冲区
                    log.write("\n")
                    log.flush()  # 手动刷新缓冲区
        # 写入统计信息到日志文件
        log.write(f"总计处理 {total_count} 个PDF文件，成功 {success_count} 个，失败 {fail_count} 个。\n")
        log.flush()  # 手动刷新缓冲区

    
    # 打印统计信息
    print(f"总计处理 {total_count} 个PDF文件，成功 {success_count} 个，失败 {fail_count} 个。")

def main():
    # 指定大文件夹路径和水印参考图片路径
    folder_path = r"C:\Users\cmy\Desktop\QCM6690 RFID Documents"  # 替换为实际的大文件夹路径
    watermark_image_path = r"C:\Users\cmy\Desktop\test\page1_img2.jpeg"
    
    # 设置相似度阈值（SSIM范围是 -1 到 1，接近 1 表示非常相似）
    similarity_threshold = 0.8
    
    # 执行文件夹处理
    process_folder(folder_path, watermark_image_path, similarity_threshold)
    
    print("所有PDF文件处理完成，处理结果已记录到 processing_log.txt")

if __name__ == "__main__":
    main()