import sys
import numpy as np
import pyzed.sl as sl
import cv2
import math


def main(): 
    zed = sl.Camera() 

    init_params = sl.InitParameters() 
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init_params.coordinate_units = sl.UNIT.MILLIMETER
    init_params.camera_resolution = sl.RESOLUTION.VGA
    # init_params.coordinate_system = 

    err = zed.open(init_params)
    if err!= sl.ERROR_CODE.SUCCESS: 
        exit(1)
    
    runtime_parameters = sl.RuntimeParameters() 
    runtime_parameters.sensing_mode = sl.SENSING_MODE.STANDARD

    runtime_parameters.confidence_threshold = 100 
    runtime_parameters.textureness_confidence_threshold = 100 

    i = 0 
    image = sl.Mat() 
    depth = sl.Mat() 
    point_cloud = sl.Mat()

    mirror_ref = sl.Transform() 
    mirror_ref.set_translation(sl.Translation(2.75,4.0,0))
    tr_np = mirror_ref.m

    while True: 

        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            image_ocv = image.get_data()
            cv2.imwrite("IMAGE.png", image_ocv)


            zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
            # image_ocv = depth.get_data()
            # cv2.imwrite("IMAGE.png", image_ocv)

            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

            x = round(image.get_width()/2)
            y = round(image.get_height()/2)
            # print(x,y)
            err, point_cloud_value = point_cloud.get_value(x,y)

            distance = math.sqrt(point_cloud_value[0] *point_cloud_value[0]+
                                 point_cloud_value[1] *point_cloud_value[1]+
                                 point_cloud_value[2] *point_cloud_value[2])

            if not np.isnan(distance) and not np.isinf(distance): 
                print(distance)
            sys.stdout.flush()

    zed.close() 

if __name__ == "__main__": 
    main()