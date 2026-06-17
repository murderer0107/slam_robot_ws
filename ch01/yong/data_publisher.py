import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GreetingPublisher(Node):
    
    def __init__(self):
        super().__init__('greeting_publisher')
        self.publisher_ = self.create_publisher(String, 'greeting', 10)
        self.timer = self.create_timer(1.0, self.ch01_send_msg)
        self.get_logger().info("Greeting Publisher started.")

    def ch01_send_msg(self):
        msg = String()
        msg.data = "Hello, ROS 2!"

        self.publisher_.publish(msg)
        self.get_logger().info(f'Published message: {msg.data}')


def main(args=None):
    rclpy.init(args=args)

    node = GreetingPublisher()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()