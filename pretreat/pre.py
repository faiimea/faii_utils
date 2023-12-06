import os
from bvhtoolbox import BvhTree
from PIL import Image
import shutil
import numpy as np

'''
Work Flow

get_bvh_info + bvh_info_filter -> filterer_info

RVM remove bgr of video in different folder,in each folder:

resize_and_center_image,cut_image,preatment (!save image?)

divide_images_as_bvh

'''

# Cut image to 64*64

def cut_image(path, cut_path, size):
    '''
    剪切图片
    :param path: 输入图片路径
    :param cut_path: 剪切图片后的输出路径
    :param size: 要剪切的图片大小
    :return:
    '''
    for (root, dirs, files) in os.walk(path):
        temp = root.replace(path, cut_path)
        if not os.path.exists(temp):
            os.makedirs(temp)
        for file in files:

            print(file)
            image, flag = cut(Image.open(os.path.join(root, file)))
            if not flag: Image.fromarray(image).convert('L').resize((size, size)).save(os.path.join(temp, file))
        #print(temp)
    pass

def cut(image):
    '''
    通过找到人的最小最大高度与宽度把人的轮廓分割出来，、
    因为原始轮廓图为二值图，因此头顶为将二值图像列相加后，形成一列后第一个像素值不为0的索引。
    同理脚底为形成一列后最后一个像素值不为0的索引。
    人的宽度也同理。
    :param image: 需要裁剪的图片 N*M的矩阵
    :return: temp:裁剪后的图片 size*size的矩阵。flag：是否是符合要求的图片
    '''
    # 找到人的最小最大高度与宽度
    height_min = (image.sum(axis=1) != 0).argmax()
    height_max = ((image.sum(axis=1) != 0).cumsum()).argmax()
    width_min = (image.sum(axis=0) != 0).argmax()
    width_max = ((image.sum(axis=0) != 0).cumsum()).argmax()
    head_top = image[height_min, :].argmax()
    # 设置切割后图片的大小，为size*size，因为人的高一般都会大于宽
    size = height_max - height_min
    temp = np.zeros((size, size))
    # 将width_max-width_min（宽）乘height_max-height_min（高，szie）的人的轮廓图，放在size*size的图片中央
    # l = (width_max-width_min)//2
    # r = width_max-width_min-l
    # 以头为中心，将将width_max-width_min（宽）乘height_max-height_min（高，szie）的人的轮廓图，放在size*size的图片中央
    l1 = head_top - width_min
    r1 = width_max - head_top
    # 若宽大于高，或头的左侧或右侧身子比要生成图片的一般要大。则此图片为不符合要求的图片
    flag = False
    if size <= width_max - width_min or size // 2 < r1 or size // 2 < l1:
        flag = True
        return temp, flag
    # centroid = np.array([(width_max+width_min)/2,(height_max+height_min)/2],dtype='int')
    temp[:, (size // 2 - l1):(size // 2 + r1)] = image[height_min:height_max, width_min:width_max]
    return temp, flag

# Get bvh frame info
def get_bvh_info(folder_path):
    bvh_info = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".bvh"):
                file_path = os.path.join(root, file)
                with open(file_path) as f:
                    bvh_tree = BvhTree(f.read())

                bvh_name = os.path.splitext(file)[0]
                nframes = bvh_tree.nframes

                bvh_info.append({"name": bvh_name, "nframes": nframes})

    return bvh_info

def bvh_info_filter(bvh_folder_path):
    # Modify here
    bvh_folder_path = "D:\dataset\Data-to-fz\cmu-walk-use"
    info = get_bvh_info(bvh_folder_path)

    for bvh in info:
        print(f"BVH Name: {bvh['name']}, nframes: {bvh['nframes']}")

    # Combine anim clip in list as person
    info.append({"name": '15', "nframes": 13401})
    info.append({"name": '17', "nframes": 12669})
    names_to_remove = ["15_01", "15_09", "17_01", "17_02"]  # 要删除的BVH名字列表
    filtered_info = [bvh for bvh in info if bvh['name'] not in names_to_remove]
    info=filtered_info

    print(len(filtered_info))
    total_nframes = sum(bvh['nframes'] for bvh in info)
    print(f"Total nframes: {total_nframes}")

    # Divide as player speed
    speed=3
    for bvh in filtered_info:
        bvh['nframes']//=speed

    # Deal with last bvh
    for bvh in filtered_info:
        if bvh['name']=='56':
            bvh['nframes']-=30 

    total_nframes = sum(bvh['nframes'] for bvh in filtered_info)
    print(f"Total nframes: {total_nframes}")
    return filtered_info  

# Remove BGR(just color)
def convert_to_black_and_white(input_path, output_path):
    # 打开图片
    img = Image.open(input_path)

    # 获取图片的宽和高
    width, height = img.size

    # 遍历每个像素
    for x in range(width):
        for y in range(height):
            # 获取像素的RGB值
            r, g, b = img.getpixel((x, y))

            # 如果不是黑色，则设置为白色
            if r >=30 and g >=30  and b >= 30:
                img.putpixel((x, y), (255, 255, 255))
            else:
                img.putpixel((x, y), (0, 0, 0))

    # 保存处理后的图片
    img.save(output_path)

# Rm BGR Process in folder
def process_images_in_folder(folder_path):
    # 确保文件夹路径以斜杠结尾
    folder_path = os.path.join(folder_path, "")

    # 遍历文件夹中的所有图片文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith((".jpg")):
            input_path = os.path.join(folder_path, file_name)
            output_path = input_path
            print(input_path)
            #convert_to_black_and_white(input_path, output_path)

# input_folder_path = r"D:\unity project\My project\dataset\mxh-221_1\216"
# process_images_in_folder(input_folder_path,input_folder_path)


# Resize Image as person for 64
def resize_and_center_image(input_path, target_size,width_time,height_time):

    original_image = Image.open(input_path)
    original_image.thumbnail((original_image.width / width_time, original_image.height / height_time))
    original_size = original_image.size
    left = (target_size[0] - original_size[0]) // 2
    top = (target_size[1] - original_size[1]) // 2
    target_image = Image.new("RGB", target_size, color="black")
    target_image.paste(original_image, (left, top))
    output_path = input_path
    target_image.save(output_path)

# Resize all images
def process_images_in_subsubsubfolders(folder_path, target_size, depth=3):
    # 递归函数，遍历文件夹及其子文件夹，直到指定深度
    def recursive_process(current_path, current_depth):
        if current_depth <= depth:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    recursive_process(item_path, current_depth + 1)
                elif item.lower().endswith(('.jpg')):
                    #print(item_path)
                    resize_and_center_image(item_path, target_size)

    recursive_process(folder_path, 0)

# folder_path = r'D:\dataset\clean_data'
# target_size = (320, 240)
# process_images_in_subsubsubfolders(folder_path, target_size)

def delete_subfolder_with_name(root_path, target_folder_name):
    for root, dirs, files in os.walk(root_path):
        for dir_name in dirs:
            parent_folder_path = os.path.join(root, dir_name)
            target_folder_path = os.path.join(parent_folder_path, target_folder_name)
            
            # 检查目标文件夹是否存在
            if os.path.exists(target_folder_path):
                shutil.rmtree(target_folder_path)
                print(f"Deleted folder: {target_folder_path}")
# 示例用法
# root_directory = r"D:\dataset\clean_data"
# target_folder_name = "017"
# delete_subfolder_with_name(root_directory, target_folder_name)

# Classify Image and Remove BGR
def divide_images_as_bvh(image_folder,image_folder_out,filtered_info):
    # 图片文件夹的路径
    image_folder = r"D:\unity project\My project\data_copy"

    # 输出文件夹的路径
    image_folder_out = r"D:\dataset\clean_data"

    # 遍历模型文件夹
    for model_folder in os.listdir(image_folder):
        model_folder_path = os.path.join(image_folder, model_folder)
        #print(model_folder)
        
        # 确保是目录
        if os.path.isdir(model_folder_path):
            
            # 遍历视角文件夹
            for view_folder in os.listdir(model_folder_path):
                #print(view_folder)
                view_folder_path = os.path.join(model_folder_path, view_folder)
                
                # 确保是目录
                if os.path.isdir(view_folder_path):
                    # process_images_in_folder(view_folder_path)
                    # print(view_folder_path)
                    for bvh in filtered_info:
                        target_folder = os.path.join(image_folder_out,  bvh['name'], model_folder, view_folder)
                        os.makedirs(target_folder, exist_ok=True)

                    # 移动图片到相应文件夹
                    id=0
                    for bvh in filtered_info:
                        target_folder = os.path.join(image_folder_out,  bvh['name'], model_folder, view_folder)
                        
                        for i in range(bvh['nframes']):
                            # 图片的命名格式为 "0000.jpg", "0001.jpg", ...
                            source_image_path = os.path.join(view_folder_path, f"{id:04d}.jpg")
                            #print(source_image_path)
                            id+=1
                            target_image_path = os.path.join(target_folder, f"{i:04d}.jpg")
                            #print(target_image_path)
                            
                            # 移动图片
                            shutil.move(source_image_path, target_image_path)
                            # Cut it
                        id+=1

def preatment(folder_path):
    for file_name in os.listdir(folder_path):
        input_path=os.path.join(folder_path,file_name)
        output_path=input_path
        #convert_to_black_and_white(input_path,input_path)
        image=Image.open(input_path)
        image_array = np.array(image)
        binary_array = image_array[:, :, 0]
        image, flag =cut(binary_array)
        if not flag: Image.fromarray(image).convert('L').resize((64, 64)).save(output_path)

def traverse_third_level_folders(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            subfolder_path = os.path.join(root, dir_name)
            subsubfolders = [subsubfolder for subsubfolder in os.listdir(subfolder_path)
                             if os.path.isdir(os.path.join(subfolder_path, subsubfolder))]
            for subsubfolder in subsubfolders:
                subsubfolder_path = os.path.join(subfolder_path, subsubfolder)
                third_level_folders = [third_level_folder for third_level_folder in os.listdir(subsubfolder_path)
                                       if os.path.isdir(os.path.join(subsubfolder_path, third_level_folder))]
                for third_level_folder in third_level_folders:
                    third_level_folder_path = os.path.join(subsubfolder_path, third_level_folder)
                    preatment(third_level_folder_path)

# 例子
# folder_path = r'D:\dataset\clean_data'
# traverse_third_level_folders(folder_path)

if __name__ == '__main__':
    process_images_in_folder(r'D:\unity project\My project\data_copy\144\0')