"""
MIT License

Copyright (c) 2017 20tab srl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import unittest

from bvhtoolbox import Bvh, BvhNode

'''
测试用例:

test_file_read: 测试从文件读取BVH数据。
test_empty_root: 测试创建一个空的BVH树。
test_tree 和 test_tree2: 测试BVH树的结构。
test_filter: 测试根据名称过滤节点。
test_bones: 测试获取骨骼信息。
test_offset: 测试获取关节的偏移量。
test_search: 测试在BVH树中搜索节点。
test_search_single_item 和 test_search_single_item_joints: 测试搜索单个节点或关节。
test_joint_offset: 测试获取关节的偏移量。
test_unknown_joint 和 test_unknown_attribute: 测试处理未知关节和属性的情况。
test_nframes_red_light, test_nframes, test_frame_time, test_nframes2, test_nframes_with_frames_list: 测试帧数和帧时间的获取。
test_channels: 测试获取关节的通道信息。
test_frame_channel 和 test_frame_channel2: 测试获取帧上的通道值。
test_frame_iteration: 测试迭代帧并累加X轴的位置值。
test_joints_names, test_joint_parent_index, test_joint_parent: 测试获取关节名称、父索引和父关节。
test_frame_joint_multi_channels 和 test_frames_multi_channels: 测试获取帧上的多通道值。
test_joint_children: 测试获取关节的直接子节点。
'''

class TestBvh(unittest.TestCase):

    def test_file_read(self):
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(len(mocap.data), 98838)

    def test_empty_root(self):
        mocap = Bvh('')
        self.assertTrue(isinstance(mocap.root, BvhNode))

    def test_tree(self):
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual([str(item) for item in mocap.root],
                         ['HIERARCHY', 'ROOT mixamorig:Hips', 'MOTION', 'Frames: 69', 'Frame Time: 0.0333333']
                         )

    def test_tree2(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual([str(item) for item in mocap.root],
                         ['HIERARCHY', 'ROOT Hips', 'MOTION', 'Frames: 455', 'Frame Time: 0.033333']
                         )

    def test_filter(self):
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual([str(item) for item in mocap.root.filter('ROOT')], ['ROOT mixamorig:Hips'])

    def test_bones(self):
        bones = []
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())

        def iterate_joints(joint):
            bones.append(str(joint))
            for child in joint.filter('JOINT'):
                iterate_joints(child)
        iterate_joints(next(mocap.root.filter('ROOT')))
        self.assertEqual(bones[0], 'ROOT mixamorig:Hips')
        self.assertEqual(bones[17], 'JOINT mixamorig:LeftHandThumb2')
        self.assertEqual(bones[22], 'JOINT mixamorig:LeftHandRing1')
        self.assertEqual(bones[30], 'JOINT mixamorig:RightForeArm')

    def test_offset(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(next(mocap.root.filter('ROOT'))['OFFSET'], ['0.0000', '0.0000', '0.0000'])

    def test_search(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual([str(node) for node in mocap.search('JOINT', 'LeftShoulder')], ['JOINT LeftShoulder'])

    def test_search_single_item(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual([str(node) for node in mocap.search('ROOT')], ['ROOT Hips'])

    def test_search_single_item_joints(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(len(mocap.search('JOINT')), 18)

    def test_joint_offset(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.joint_offset('RightElbow'), (-2.6865, -25.0857, 1.2959))

    def test_unknown_joint(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        with self.assertRaises(LookupError):
            mocap.joint_offset('FooBar')

    def test_unknown_attribute(self):
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())
        with self.assertRaises(IndexError):
            mocap.root['Broken']

    def test_nframes_red_light(self):
        mocap = Bvh('')
        with self.assertRaises(LookupError):
            mocap.nframes

    def test_nframes(self):
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.nframes, 69)

    def test_frame_time(self):
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.frame_time, 0.0333333)

    def test_nframes2(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.nframes, 455)

    def test_nframes_with_frames_list(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.nframes, len(mocap.frames))

    def test_channels(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.joint_channels('LeftElbow'), ['Zrotation', 'Xrotation', 'Yrotation'])
        self.assertEqual(mocap.joint_channels('Hips'),
                         ['Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Xrotation', 'Yrotation']
                         )

    def test_frame_channel(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.frame_joint_channel(22, 'Hips', 'Xrotation'), -20.98)
        self.assertEqual(mocap.frame_joint_channel(22, 'Chest', 'Xrotation'), 17.65)
        self.assertEqual(mocap.frame_joint_channel(22, 'Neck', 'Xrotation'), -6.77)
        self.assertEqual(mocap.frame_joint_channel(22, 'Head', 'Yrotation'), 8.47)

    def test_frame_channel2(self):
        with open('tests/example_files/test_freebvh.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.frame_joint_channel(22, 'mixamorig:Hips', 'Xposition'), 4.3314)

    def test_frame_iteration(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        x_accumulator = 0.0
        for i in range(0, mocap.nframes):
            x_accumulator += mocap.frame_joint_channel(i, 'Hips', 'Xposition')
        self.assertTrue(abs(-19735.902699999995 - x_accumulator) < 0.0001)

    def test_joints_names(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.get_joints_names()[17], 'RightKnee')

    def test_joint_parent_index(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.joint_parent_index('Hips'), -1)
        self.assertEqual(mocap.joint_parent_index('Chest'), 0)
        self.assertEqual(mocap.joint_parent_index('LeftShoulder'), 3)

    def test_joint_parent(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.joint_parent('Chest').name, 'Hips')

    def test_frame_joint_multi_channels(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        rotation = mocap.frame_joint_channels(30, 'Head', ['Xrotation', 'Yrotation', 'Zrotation'])
        self.assertEqual(rotation, [1.77, 13.94, -7.42])

    def test_frames_multi_channels(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        rotations = mocap.frames_joint_channels('Head', ['Xrotation', 'Yrotation', 'Zrotation'])
        self.assertEqual(len(rotations), mocap.nframes)

    def test_joint_children(self):
        with open('tests/example_files/test_mocapbank.bvh') as f:
            mocap = Bvh(f.read())
        self.assertEqual(mocap.joint_direct_children('Chest')[0].name, 'Chest2')
        self.assertEqual(mocap.joint_direct_children('Hips')[0].name, 'Chest')
        self.assertEqual(mocap.joint_direct_children('Hips')[1].name, 'LeftHip')
        self.assertEqual(mocap.joint_direct_children('Hips')[2].name, 'RightHip')
        self.assertEqual(mocap.joint_direct_children('RightWrist'), [])


if __name__ == '__main__':
    unittest.main()
