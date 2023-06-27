import os
import numpy as np
import trimesh
import pyrender
import matplotlib.pyplot as plt
import json
import cv2
from trimesh import Trimesh

from pyrender import PerspectiveCamera,\
                     DirectionalLight, SpotLight, PointLight,\
                     MetallicRoughnessMaterial,\
                     Primitive, Mesh, Node, Scene,\
                     OffscreenRenderer

def random_camera_pose():

    theta = np.random.uniform(low=0.0, high=2*np.pi)
    phi = np.random.uniform(low=0.0, high=np.pi)
    x = ra * np.sin(phi) * np.cos(theta)
    y = ra * np.sin(phi) * np.sin(theta)
    z = ra * np.cos(phi)
    camera_position = np.array([x, y, z])

    camera_direction = -camera_position / np.linalg.norm(camera_position)

    z_axis = -1 * camera_direction
    up_vector = np.array([0, 1, 0]) 
    x_axis = np.cross(up_vector, z_axis)
    x_axis /= np.linalg.norm(x_axis)
    y_axis = np.cross(z_axis, x_axis)
    y_axis /= np.linalg.norm(y_axis)

    rotation_matrix = np.eye(3)
    rotation_matrix[:, 0] = x_axis
    rotation_matrix[:, 1] = y_axis
    rotation_matrix[:, 2] = z_axis

    translation_vector = camera_position
    camera_pose = np.eye(4)
    camera_pose[:3, :3] = rotation_matrix
    camera_pose[:3, 3] = translation_vector

    return camera_pose


object_names = [
    'fuze',
    'drill',
    'car',
    'coffee cup',
    'table',
    'weapon'
]
file_formats = ['.obj', '.obj', '.obj', '.obj', '.ply', '.ply']
radius = [0.5, 0.5, 5, 3, 3, 30]
image_number = 10
ra = 0
# camera
cam = PerspectiveCamera(yfov=(np.pi / 3.0))
nc = pyrender.Node(camera=cam, matrix=np.eye(4))
camera_poses = {}

# Light
light = DirectionalLight(color=[1.0, 1.0, 1.0], intensity=7.0)
nl = Node(light=light, matrix=np.eye(4))

# Scene
scene = Scene(ambient_light=np.array([0.02, 0.02, 0.02, 1.0]))
scene.add_node(nc)
scene.add_node(nl)

for j in range(len(object_names)):
    ra = radius[j]
    os.makedirs(object_names[j], exist_ok=True)
    # object
    object_trimesh = trimesh.load('./models/' + object_names[j] + file_formats[j])
    object_mesh = pyrender.Mesh.from_trimesh(object_trimesh)
    object_node = pyrender.Node(mesh=object_mesh)
    scene.add_node(object_node)
    object_camera_poses = {}
    for i in range(image_number):
        cam_pose = random_camera_pose()
        object_camera_poses["pose" + str(i + 1)] = cam_pose.tolist()
        scene.set_pose(nc, pose=cam_pose)
        scene.set_pose(nl, pose=cam_pose)
        r = OffscreenRenderer(viewport_width=640*2, viewport_height=480*2)
        color, depth = r.render(scene)
        r.delete()
        cv2.imwrite(object_names[j] + '/image' + str(i + 1) + '.png', color)
        #pyrender.Viewer(scene, use_raymond_lighting=True)
    scene.remove_node(object_node)
        # Store object camera poses in the main camera_poses dictionary
    camera_poses[object_names[j]] = object_camera_poses

with open('camera_poses.json', 'w') as json_file:
    json.dump(camera_poses, json_file, indent=4)