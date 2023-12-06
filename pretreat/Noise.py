import numpy as np
from bvhtoolbox import BvhTree
import os
import copy

def add_gaussian_noise(data, noise_columns, mean=0, std=0.01):
    data_array = np.array(data, dtype=float)
    noise = np.random.normal(mean, std, data_array.shape)
    noisy_data = data_array + noise
    noisy_data[:, noise_columns] = data_array[:, noise_columns]
    return noisy_data.tolist()

def add_laplace_noise(data, noise_columns, loc=0, scale=0.01):
    data_array = np.array(data, dtype=float)
    noise = np.random.laplace(loc, scale, data_array.shape)
    noisy_data = data_array + noise
    noisy_data[:, noise_columns] = data_array[:, noise_columns]
    return noisy_data.tolist()

def add_cauchy_noise(data, noise_columns, loc=0, scale=0.01):
    data_array = np.array(data, dtype=float)
    noise = np.random.standard_cauchy(data_array.shape) * scale + loc
    noisy_data = data_array + noise
    noisy_data[:, noise_columns] = data_array[:, noise_columns]
    return noisy_data.tolist()

def get_joint_index(data, name):
    return data.get_joints(end_sites=False).index(data.get_joint(name))

def modify_bvh(input_folder, output_folder):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".bvh"):
                input_path = os.path.join(root, file)

                with open(input_path) as f:
                    mocap = BvhTree(f.read())
                mocap.frames = [[float(value) for value in frame] for frame in mocap.frames]
                all_joints = mocap.get_joints_names()
                selected_joints = [joint for joint in all_joints if 'LeftHand' in joint or 'RightHand' in joint or 'Head' in joint]
                selected_joints_index = []

                for i in selected_joints:
                    selected_joints_index.append(get_joint_index(mocap, i))

                changed_joints_index = [0, 1, 2]

                for i in selected_joints_index:
                    changed_joints_index.append(3 + int(i * 3))
                    changed_joints_index.append(4 + int(i * 3))
                    changed_joints_index.append(5 + int(i * 3))

                noise_index=[0.001,0.01,0.1]

                copy_frame=copy.deepcopy(mocap.frames)

                for i in noise_index:
                  copy_frame.extend(add_gaussian_noise(mocap.frames, changed_joints_index, std=i))
                for i in noise_index:
                  copy_frame.extend(add_laplace_noise(mocap.frames, changed_joints_index, scale=i))
                for i in noise_index:
                  copy_frame.extend(add_cauchy_noise(mocap.frames, changed_joints_index, scale=i))

                # 将浮点数转换为字符串
                mocap.frames=copy_frame
                mocap.frames = [['{:.6f}'.format(value) for value in frame] for frame in mocap.frames]

                total_frames=mocap.nframes*10

                output_path = os.path.join(output_folder, file)

                mocap.write_file(output_path)
                print(output_path)


                # Read the merged bvh file
                with open(output_path, 'r') as f:
                    lines = f.readlines()

                # Find the line starting with 'Frames:'
                for i, line in enumerate(lines):
                    if line.startswith('Frames:'):
                        # Modify the number after 'Frames:'
                        lines[i] = 'Frames: {}\n'.format(total_frames)
                        break

                # Write the modified lines back to the file
                with open(output_path, 'w') as f:
                    f.writelines(lines)

if __name__ == '__main__':
    input_folder = 'D:\Data-to-fz\cmu-walk'
    output_folder = 'D:\Data-to-fz\cmu-walk-noise'
    modify_bvh(input_folder, output_folder)
