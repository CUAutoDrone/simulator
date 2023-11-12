#!/usr/bin/env python
import rospy
from mavros_msgs.srv import CommandBool, SetMode
from mavros_msgs.msg import State
from geometry_msgs.msg import Twist

current_state = State()

def state_cb(state):
    global current_state
    current_state = state

if __name__ == "__main__":
    rospy.init_node('drone_control', anonymous=True)

    rospy.Subscriber("mavros/state", State, state_cb)
    local_vel_pub = rospy.Publisher('mavros/setpoint_velocity/cmd_vel_unstamped', Twist, queue_size=10)

    # Wait for FCU connection
    while not current_state.connected:
        rospy.sleep(0.1)

    # Arm the drone
    rospy.wait_for_service('mavros/cmd/arming')
    try:
        armService = rospy.ServiceProxy('mavros/cmd/arming', CommandBool)
        armService(True)
    except rospy.ServiceException as e:
        print("Service arming call failed: %s" % e)

    # Set to offboard mode
    rospy.wait_for_service('mavros/set_mode')
    try:
        flightModeService = rospy.ServiceProxy('mavros/set_mode', SetMode)
        flightModeService(custom_mode='OFFBOARD')
    except rospy.ServiceException as e:
        print("Service set_mode call failed: %s" % e)

    # Send a few setpoints before starting
    for i in range(100):
        local_vel_pub.publish(Twist())
        rospy.sleep(0.1)

    # Control the drone
    vel_msg = Twist()
    vel_msg.linear.x = 1.0
    vel_msg.linear.y = 0.0
    vel_msg.linear.z = 0.0

    while not rospy.is_shutdown():
        local_vel_pub.publish(vel_msg)
        rospy.sleep(0.1)
