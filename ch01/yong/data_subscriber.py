import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class GreetingSubscriber(Node):
    
    def __init__(self):
        super().__init__('greeting_subscriber')
        self.subscription = self.create_subscription(
            String,
            'greeting',
            self.listener_callback,
            10
        )
        self.get_logger().info("Greeting Subscriber started.")

    def listener_callback(self, msg):
        self.get_logger().info(f'Received greeting: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = GreetingSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
