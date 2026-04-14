import fitz  # PyMuPDF
import os
import io
from PIL import Image

# 设置PDF文件路径（请根据实际情况修改）
pdf_path = r"C:\Users\cmy\Desktop\QCM6690 RFID Documents\80-88966-14_REV_AB_RFID_Hardware_Application_Note.pdf"
# 设置图片保存目录（请根据实际情况修改）
output_folder = r"C:\Users\cmy\Desktop\test"

def extract_images_from_pdf(pdf_path, output_folder):
    """从PDF文件中提取所有图片并保存到指定文件夹"""
    
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 用于存储提取的图片数量
    image_count = 0
    
    # 遍历PDF的每一页
    for page_index in range(len(pdf_document)):
        # 获取当前页的所有图片
        image_list = pdf_document[page_index].get_images(full=True)
        
        # 打印当前页的图片数量
        if image_list:
            print(f"[+] 第 {page_index + 1} 页找到 {len(image_list)} 张图片")
        else:
            print(f"[!] 第 {page_index + 1} 页未找到图片")
        
        # 遍历当前页的所有图片
        for image_index, img in enumerate(image_list, start=1):
            # 获取图片的XREF编号
            xref = img[0]
            
            # 提取图片的基本信息
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]  # 图片数据
            image_ext = base_image["ext"]  # 图片扩展名
            
            # 生成图片文件名
            image_name = f"page{page_index + 1}_img{image_index}.{image_ext}"
            image_path = os.path.join(output_folder, image_name)
            
            # 保存图片
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            # 尝试打开图片以验证其有效性
            try:
                img = Image.open(io.BytesIO(image_bytes))
                img.verify()  # 验证图片完整性
                print(f"[+] 成功提取图片: {image_name} (尺寸: {img.size})")
                image_count += 1
            except Exception as e:
                print(f"[!] 提取图片失败: {image_name} - {str(e)}")
                # 删除无效图片
                if os.path.exists(image_path):
                    os.remove(image_path)
    
    # 关闭PDF文件
    pdf_document.close()
    
    print(f"\n[+] 提取完成！共提取出 {image_count} 张有效图片，已保存到 {output_folder} 文件夹")

# 执行图片提取
extract_images_from_pdf(pdf_path, output_folder)
