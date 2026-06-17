import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class CameraSubscriber(Node):

    def __init__(self):
        super().__init__("camera_subscriber")
        self.subscription = self.create_subscription(
            Image,
            "camera/image_raw",
            self.listener_callback,
            10
        )
        self.bridge = CvBridge()

    def listener_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        # cv2.imshow("Camera Feed", frame)
        cv2.waitKey(1)
    # def listener_callback(self, msg):
    #     frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

    #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     edge = cv2.Canny(gray, 30, 200)

    #     cv2.imshow("Original Camera", frame)
    #     cv2.imshow("Canny Edge Camera", edge)

    #     cv2.waitKey(1)

        


def main():
    rclpy.init()
    node = CameraSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    main()