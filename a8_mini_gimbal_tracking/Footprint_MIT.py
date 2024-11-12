import numpy as np
import math
import utm


def getPos(
    latitude,
    longitude,
    alt,
    bear,
    Ls,
    Hs,
    f,
    tilt_cam,
    roll,
    target_x,
    target_y,
    rad1,
    width,
    height,
):
    x, y = target_x, target_y

    if True:
        width_pixel = width
        height_pixel = height
        temp_x = width_pixel / 6000
        temp_y = height_pixel / 3376

        X0_latitude = latitude
        Y0_longitude = longitude

        pitch_cam = float(tilt_cam)

        cam_pitch = (pitch_cam) * rad1
        cam_roll = roll * rad1
        cam_yaw = bear * rad1
        H = alt

        var = utm.from_latlon(X0_latitude, Y0_longitude)
        X0 = var[0]
        Y0 = var[1]
        zone = var[2]
        zone_block = var[3]

        # x1 = Ls / 2
        # y1 = Hs / 2

        # # Corner up left
        # x2 = -Ls / 2
        # y2 = Hs / 2

        # # Corner down left
        # x3 = -Ls / 2
        # y3 = -Hs / 2

        # # Corner down right
        # x4 = Ls / 2
        # y4 = -Hs / 2


        w = width_pixel / 2
        h = height_pixel / 2

        x5 = int(x * temp_x)  # 1.6798
        y5 = int(y * temp_y)  # 1.992
        pixel_width_in = x5
        pixel_height_in = y5

        if pixel_width_in < w and pixel_height_in < h:
            x_pixel = (Ls / width_pixel) * pixel_width_in
            x_pixel = -((Ls / 2) - x_pixel)
            y_pixel = (Hs / height_pixel) * pixel_height_in
            y_pixel = (Hs / 2) - y_pixel

        elif pixel_width_in > w and pixel_height_in < h:
            rem_pixel = pixel_width_in - (width_pixel / 2)
            x_pixel_req = (Ls / width_pixel) * rem_pixel
            x_pixel = x_pixel_req
            y_pixel = (Hs / height_pixel) * pixel_height_in
            y_pixel = (Hs / 2) - y_pixel

        elif pixel_width_in < w and pixel_height_in > h:
            x_pixel = (Ls / width_pixel) * pixel_width_in
            x_pixel = -((Ls / 2) - x_pixel)
            rem_pixel = pixel_height_in - (height_pixel / 2)
            y_pixel_req = (Hs / height_pixel) * rem_pixel
            y_pixel = -y_pixel_req

        elif pixel_width_in > w and pixel_height_in > h:

            x_rem_pixel = pixel_width_in - (width_pixel / 2)
            y_rem_pixel = pixel_height_in - (height_pixel / 2)

            x_pixel = (Ls / width_pixel) * x_rem_pixel
            x_pixel = x_pixel
            y_pixel = (Hs / height_pixel) * y_rem_pixel
            y_pixel = -y_pixel

        elif pixel_width_in == w and pixel_height_in < h:
            x_pixel = 0

            y_pixel = (Hs / height_pixel) * pixel_height_in
            y_pixel = (Hs / 2) - y_pixel

        elif pixel_width_in == w and pixel_height_in == h:
            x_pixel = 0
            y_pixel = 0
        else:
            x_pixel = 0
            y_pixel = 0
        m11 = math.cos(cam_roll) * math.cos(cam_yaw)
        m12 = -math.cos(cam_roll) * math.sin(cam_yaw)
        m13 = math.sin(cam_roll)
        m21 = math.cos(cam_pitch) * math.sin(cam_yaw) + math.sin(cam_pitch) * math.sin(
            cam_roll
        ) * math.cos(cam_yaw)
        m22 = math.cos(cam_pitch) * math.cos(cam_yaw) - math.sin(cam_pitch) * math.sin(
            cam_roll
        ) * math.sin(cam_yaw)
        m23 = -math.sin(cam_pitch) * math.cos(cam_roll)
        m31 = math.sin(cam_pitch) * math.sin(cam_yaw) - math.cos(cam_pitch) * math.sin(
            cam_roll
        ) * math.cos(cam_yaw)
        m32 = math.sin(cam_pitch) * math.cos(cam_yaw) + math.cos(cam_pitch) * math.sin(
            cam_roll
        ) * math.sin(cam_yaw)
        m33 = math.cos(cam_pitch) * math.cos(cam_roll)

        # X1 = (
        #     -H * ((m11 * x1 + m21 * y1 - m31 * f) / (m13 * x1 + m23 * y1 - m33 * f))
        #     + X0
        # )
        # Y1 = (
        #     -H * ((m12 * x1 + m22 * y1 - m32 * f) / (m13 * x1 + m23 * y1 - m33 * f))
        #     + Y0
        # )
        # X2 = (
        #     -H * ((m11 * x2 + m21 * y2 - m31 * f) / (m13 * x2 + m23 * y2 - m33 * f))
        #     + X0
        # )
        # Y2 = (
        #     -H * ((m12 * x2 + m22 * y2 - m32 * f) / (m13 * x2 + m23 * y2 - m33 * f))
        #     + Y0
        # )
        # X3 = (
        #     -H * ((m11 * x3 + m21 * y3 - m31 * f) / (m13 * x3 + m23 * y3 - m33 * f))
        #     + X0
        # )
        # Y3 = (
        #     -H * ((m12 * x3 + m22 * y3 - m32 * f) / (m13 * x3 + m23 * y3 - m33 * f))
        #     + Y0
        # )
        # X4 = (
        #     -H * ((m11 * x4 + m21 * y4 - m31 * f) / (m13 * x4 + m23 * y4 - m33 * f))
        #     + X0
        # )
        # Y4 = (
        #     -H * ((m12 * x4 + m22 * y4 - m32 * f) / (m13 * x4 + m23 * y4 - m33 * f))
        #     + Y0
        # )

        X_R = (
            -H
            * (
                (m11 * x_pixel + m21 * y_pixel - m31 * f)
                / (m13 * x_pixel + m23 * y_pixel - m33 * f)
            )
            + X0
        )
        Y_R = (
            -H
            * (
                (m12 * x_pixel + m22 * y_pixel - m32 * f)
                / (m13 * x_pixel + m23 * y_pixel - m33 * f)
            )
            + Y0
        )

        X_C = -H * ((m11 * 0 + m21 * 0 - m31 * f) / (m13 * 0 + m23 * 0 - m33 * f)) + X0
        Y_C = -H * ((m12 * 0 + m22 * 0 - m32 * f) / (m13 * 0 + m23 * 0 - m33 * f)) + Y0

        # utm_latlon_1 = utm.to_latlon(X1, Y1, zone, zone_block)
        # lat_1 = utm_latlon_1[0]
        # lon_1 = utm_latlon_1[1]

        # utm_latlon_2 = utm.to_latlon(X2, Y2, zone, zone_block)
        # lat_2 = utm_latlon_2[0]
        # lon_2 = utm_latlon_2[1]


        # utm_latlon_3 = utm.to_latlon(X3, Y3, zone, zone_block)
        # lat_3 = utm_latlon_3[0]
        # lon_3 = utm_latlon_3[1]
        # utm_latlon_4 = utm.to_latlon(X4, Y4, zone, zone_block)
        # lat_4 = utm_latlon_4[0]
        # lon_4 = utm_latlon_4[1]


        utm_latlon_c = utm.to_latlon(X_C, Y_C, zone, zone_block)
        t_lat_c = round(utm_latlon_c[0], 9)
        t_lon_c = round(utm_latlon_c[1], 9)

        utm_latlon_r = utm.to_latlon(X_R, Y_R, zone, zone_block)
        t_lat = round(utm_latlon_r[0], 9)
        t_lon = round(utm_latlon_r[1], 9)

        R = 6371000

        latitude_diff = (t_lat - X0_latitude) * rad1
        longitude_diff = (t_lon - Y0_longitude) * rad1

        a = (np.sin(latitude_diff / 2) * np.sin(latitude_diff / 2)) + np.cos(
            X0_latitude * rad1
        ) * np.cos(t_lat * rad1) * (
            np.sin(longitude_diff / 2) * np.sin(longitude_diff / 2)
        )

        c = 2 * math.atan2(np.sqrt(a), np.sqrt(1 - a))
        distance_btw_target_vehicle = R * c
        distance_from_cam = np.sqrt(
            (H * H) + (distance_btw_target_vehicle * distance_btw_target_vehicle)
        )
        distance_from_cam = round(distance_from_cam, 3)
        distance_btw_target_vehicle = round(distance_btw_target_vehicle, 3)

        return (
            t_lat,
            t_lon
        )
