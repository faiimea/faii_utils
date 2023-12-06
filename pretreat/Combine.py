import os
from bvhtoolbox import BvhTree

def merge_bvhs(input_folder, output_path):
    merged_bvh = None
    total_frames = 0

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".bvh"):
                file_path = os.path.join(root, file)
                with open(file_path) as f:
                    bvh_tree = BvhTree(f.read())
                
                if merged_bvh is None:
                    merged_bvh = bvh_tree
                else:
                    # Ensure the hierarchy of the second bvh is compatible
                    if merged_bvh.get_joints_names() != bvh_tree.get_joints_names():
                        raise ValueError("Incompatible BVH hierarchies.")

                    # Update the total number of frames
                    total_frames += bvh_tree.nframes

                    # Add the frames of the second bvh to the merged bvh
                    merged_bvh.frames.extend(bvh_tree.frames)

    # Write the merged bvh to a new file
    merged_bvh.write_file(output_path)

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
    
# Example usage:


def merge_bvhs_by_subject(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Dictionary to store merged BVHs by subject
    merged_bvhs = {}
    merged_nframes = {}

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".bvh"):
                file_path = os.path.join(root, file)
                print(file_path)
                with open(file_path) as f:
                    bvh_tree = BvhTree(f.read())

                # Extract subject and action information from the file name
                subject, action = file.split('_')
                subject = subject.strip()
                action = action.split('.')[0].strip()

                # Create a unique key for the subject in the merged_bvhs dictionary
                key = subject

                # If the key doesn't exist in the dictionary, create a new entry
                if key not in merged_bvhs:
                    merged_bvhs[key] = bvh_tree
                    merged_nframes[key] = bvh_tree.nframes

                # Otherwise, append the frames of the current BVH to the existing entry
                else:
                    merged_bvhs[key].frames.extend(bvh_tree.frames)
                    merged_nframes[key]+=bvh_tree.nframes

    # Write the merged BVHs to the output folder
    for key, merged_bvh in merged_bvhs.items():
        output_path = os.path.join(output_folder, f"{key}.bvh")
        merged_bvh.write_file(output_path)
         # Read the merged bvh file
        print(output_path)
        with open(output_path, 'r') as f:
            lines = f.readlines()

        # Find the line starting with 'Frames:'
        for i, line in enumerate(lines):
            if line.startswith('Frames:'):
                # Modify the number after 'Frames:'
                lines[i] = 'Frames: {}\n'.format(merged_nframes[key])
                break

        # Write the modified lines back to the file
        with open(output_path, 'w') as f:
            f.writelines(lines)

# Example usage:
input_folder = "E:\datasets\Data-to-fz\cmu-walk"
output_folder = "E:\datasets\Data-to-fz\cmu-walk-out"

merge_bvhs_by_subject(input_folder, output_folder)
