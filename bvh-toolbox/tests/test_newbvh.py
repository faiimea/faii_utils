import numpy as np
import bvhtoolbox as bt
from bvhtoolbox import Bvh, BvhNode,BvhTree

def add_gaussian_noise(data, noise_columns, mean=0, std=0.01):
    noise = np.random.normal(mean, std, data.shape)
    noisy_data = data + noise
    noisy_data[:, noise_columns] = data[:, noise_columns]
    return noisy_data

def add_laplace_noise(data, loc=0, scale=1):
    noise = np.random.laplace(loc, scale, data.shape)
    noisy_data = data + noise
    return noisy_data

def add_cauchy_noise(data, loc=0, scale=1):
    noise = np.random.standard_cauchy(data.shape) * scale + loc
    noisy_data = data + noise
    return noisy_data


def get_joint_index(data,name):
        return data.get_joints(end_sites=False).index(data.get_joint(name))

def modify_bvh(path):
    with open(path) as f:
                mocap = BvhTree(f.read())
    frames=bt.get_motion_data(mocap)
    all_joints = mocap.get_joints_names()
    selected_joints = [joint for joint in all_joints if 'LeftHand' in joint or 'RightHand' in joint or 'Head' in joint]
    selected_joints_index=[]
    for i in selected_joints:
        selected_joints_index.append(get_joint_index(mocap,i))
    changed_joints_index=[]
    changed_joints_index+=[0,1,2]
    for i in selected_joints_index:
        changed_joints_index.append(3+int(i*3))
        changed_joints_index.append(4+int(i*3))
        changed_joints_index.append(5+int(i*3))
    frames=add_gaussian_noise(frames,changed_joints_index)
    bt.set_motion_data(mocap,frames)
    mocap.write_file('example_files/test_freebvh_out.bvh')

if __name__ == '__main__':
    modify_bvh('07_04.bvh')