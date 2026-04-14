import cv2
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt

def compare_images(imageA, imageB, title):
    # 计算两张图片的结构相似性指数(SSIM)
    score = ssim(imageA, imageB)
    
    # 设置显示中文
    plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
    
    # 创建一个新的图形窗口
    fig = plt.figure(title)
    plt.suptitle(f"相似度: {score:.4f}")
    
    # 显示第一张图片
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(imageA, cmap = plt.cm.gray)
    plt.title("第一张图片")
    plt.axis("off")
    
    # 显示第二张图片
    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(imageB, cmap = plt.cm.gray)
    plt.title("第二张图片")
    plt.axis("off")
    
    # 显示图形
    plt.show()
    
    return score

def main():
    # 指定图片路径
    image_path1 = r"D:\Users\cmy\Desktop\test\page1_5_A.png"
    image_path2 = r"D:\Users\cmy\Desktop\test\diff.png"
    
    try:
        # 加载图片
        image1 = cv2.imread(image_path1)
        image2 = cv2.imread(image_path2)
        
        # 检查图片是否成功加载
        if image1 is None or image2 is None:
            print("错误: 无法加载一张或两张图片。请检查文件路径。")
            return
        
        # 将图片转换为灰度图
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        
        # 确保两张图片具有相同的尺寸
        if gray1.shape != gray2.shape:
            gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
        
        # 比较图片并显示结果
        similarity_score = compare_images(gray1, gray2, "图片相似度比较")
        print(f"图片相似度得分: {similarity_score:.4f}")
        print("得分范围从-1到1，其中1表示完全相同，-1表示完全不同。")
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
