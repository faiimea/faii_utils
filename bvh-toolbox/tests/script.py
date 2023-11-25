import bpy
import os

# 设置文件夹路径
folder_path_bvh = 'D:\dataset\\test_script\\bvh'
folder_path_mhx = 'D:\dataset\\test_script\\mhx2'

# 获取所有的 BVH 文件和 MHX2 文件
bvh_files = sorted([f for f in os.listdir(folder_path_bvh) if f.endswith('.bvh')])
mhx2_files = sorted([f for f in os.listdir(folder_path_mhx) if f.endswith('.mhx2')])

# 创建一个新的场景，用于合并所有动作
bpy.ops.scene.new(type='NEW')

# 遍历每个 BVH 文件
for bvh_file in bvh_files:
    # 构建完整的文件路径
    bvh_path = os.path.join(folder_path_bvh, bvh_file)
    
    # 导入 BVH 文件到场景中
    bpy.ops.import_anim.bvh(filepath=bvh_path)

    # 获取导入的动作
    action_name = bpy.context.object.animation_data.action.name

    # 将动作添加到新场景中
    bpy.data.scenes[1].timeline_markers.new(action_name, frame=bpy.context.scene.frame_end + 1)
    bpy.data.scenes[1].timeline_markers[-1].action = bpy.data.actions[action_name]

    # 删除导入的 BVH 动作，准备导入下一个 BVH 文件
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[bpy.context.object.name].select_set(True)
    bpy.ops.object.delete()

# 遍历每个 MHX2 文件
for mhx2_file in mhx2_files:
    # 构建完整的文件路径
    mhx2_path = os.path.join(folder_path_mhx, mhx2_file)

    # 导入 MHX2 文件到场景中
    bpy.ops.import_scene.makehuman_mhx2(filepath=mhx2_path)

    # 合并所有动作到 MHX2 角色对象上
    for marker in bpy.data.scenes[1].timeline_markers:
        bpy.data.scenes[1].frame_set(marker.frame)
        bpy.context.view_layer.objects.active = bpy.data.objects[marker.action.name]
        bpy.ops.object.action_pushdown(group=True)
    
    # 将合并后的动作保存为 FBX 文件
    fbx_output_path = os.path.splitext(mhx2_path)[0] + '_merged.fbx'
    bpy.ops.export_scene.fbx(filepath=fbx_output_path, use_selection=True)

    # 删除导入的 MHX2 角色对象，准备导入下一个 MHX2 文件
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[bpy.context.object.name].select_set(True)
    bpy.ops.object.delete()

# 删除新场景
bpy.ops.scene.select_all(action='DESELECT')
bpy.data.scenes[1].select_set(True)
bpy.ops.scene.delete()
