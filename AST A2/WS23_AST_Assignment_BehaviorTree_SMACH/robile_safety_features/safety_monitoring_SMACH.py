#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import smach
from smach_ros import IntrospectionServer
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import yaml
import time

class MonitorBatteryAndCollision(smach.State):
    def __init__(self, node):
        super(MonitorBatteryAndCollision, self).__init__(outcomes=['low_battery', 'collision', 'normal'])

        # TODO: Define class variables and set up necessary publishers/subscribers
        self.node = node
        self.battery_subscriber = self.node.create_subscription(String, '/battery_topic', self.battery_callback, 10)
        self.collision_subscriber = self.node.create_subscription(LaserScan, '/scan', self.collision_callback, 10)
        self.battery_threshold = 30.0  #threshold for low battery
        self.collision_threshold = 0.2  #threshold for collision detection

    def battery_callback(self, msg):
        # TODO: Implement logic to check battery level and set appropriate outcomes
        battery_level = float(msg.data)
        if battery_level < self.battery_threshold:
            self.node.get_logger().info('Low battery detected!')
            self.node.get_logger().info('Battery level: {}'.format(battery_level))
            self.node.get_logger().info('Stopping...')
            return 'low_battery'
        return 'normal'

    def collision_callback(self, msg):
        # TODO: Implement logic to check for collisions and set appropriate outcomes
        min_distance = min(msg.ranges)
        if min_distance < self.collision_threshold:
            self.node.get_logger().info('Collision detected!')
            self.node.get_logger().info('Stopping...')
            self.node.get_logger().info('Transitioning to collision state')
            return 'collision'
        return 'normal'

    def execute(self, userdata):
        # TODO: Implement state execution logic and return outcome
        self.node.get_logger().info('Executing MonitorBatteryAndCollision state...')
        twist = Twist() # Publish a Twist message to stop the robot
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.node.get_logger().info('Publishing Twist message to stop the robot...')
        # TODO: Publish the twist message
        return 'normal'


class RotateBase(smach.State):
    def __init__(self, node):
        super(RotateBase, self).__init__(outcomes=['rotate_complete', 'normal'])

        # TODO: Define class variables and set up necessary publishers/subscribers
        self.node = node
        self.rotate_publisher = self.node.create_publisher(Twist, '/cmd_vel', 10)

    def execute(self, userdata):
        # TODO: Implement state execution logic and return outcome
        self.node.get_logger().info('Executing RotateBase state...')
        # Example: Publish a Twist message to rotate the robot
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.5  # Example angular velocity for rotation
        self.node.get_logger().info('Publishing Twist message to rotate the robot...')
        # TODO: Publish the twist message
        return 'rotate_complete'


def main(args=None):
    rclpy.init(args=args)
    node = Node('smach_example_node')

    # TODO: Create the state machine, add states, and define transitions
    sm = smach.StateMachine(outcomes=['outcome'])

    with sm:
        smach.StateMachine.add('IDLE', Idle(node), transitions={'activated': 'MONITOR_BATTERY_COLLISION'})
        smach.StateMachine.add('MONITOR_BATTERY_COLLISION', MonitorBatteryAndCollision(node),
                               transitions={'low_battery': 'ROTATE_BASE',
                                            'collision': 'MONITOR_BATTERY_COLLISION',
                                            'normal': 'MONITOR_BATTERY_COLLISION'})
        smach.StateMachine.add('ROTATE_BASE', RotateBase(node),
                               transitions={'rotate_complete': 'MONITOR_BATTERY_COLLISION',
                                            'normal': 'MONITOR_BATTERY_COLLISION'})

    # Create and start the introspection server (for visualizing the state machine)
    sis = IntrospectionServer('smach_server', sm, '/SM_ROOT')
    sis.start()

    # Execute the state machine
    outcome = sm.execute()

    # Wait for the introspection server to complete
    sis.stop()

    rclpy.shutdown()

if __name__ == '__main__':
    main()
'''
#Reference - 
CalStateLA ASME
https://wiki.ros.org/smach/Tutorials

'''