

from pymavlink import mavutil

#from dronekit import connect, VehicleMode, LocationGlobalRelative
# uav1 = connect('udpin:0.0.0.0:14550', wait_ready=True) 
master = mavutil.mavlink_connection("udpin:0.0.0.0:14550", baud=115200)




while True:
    # Fetch GLOBAL_POSITION_INT message
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
    
    if msg:
        # Latitude and Longitude are in 1e7 format
        mod_lat = msg.lat / 1e7  # Convert to decimal degrees
        mod_lng = msg.lon / 1e7  # Convert to decimal degrees
        rel_alt = msg.relative_alt / 1000  # Relative altitude in meters (divide by 1000)

        print(f"Latitude: {mod_lat}, Longitude: {mod_lng}, Relative Altitude: {rel_alt} meters")
    
    # Fetch ATTITUDE message for yaw, roll, and pitch
    attitude_msg = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)

    if attitude_msg:
        mod_yaw_angle = attitude_msg.yaw * (180 / 3.14159)  # Convert from radians to degrees
        mod_roll = attitude_msg.roll * (180 / 3.14159)      # Convert from radians to degrees
        mod_pitch = attitude_msg.pitch * (180 / 3.14159)    # Convert from radians to degrees

        print(f"Yaw: {mod_yaw_angle:.2f}°, Roll: {mod_roll:.2f}°, Pitch: {mod_pitch:.2f}°")