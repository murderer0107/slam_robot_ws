# depth_checker_node.py

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge

import numpy as np
import cv2


# ================================
# 기본 설정
# ================================
ROBOT_ID = 8

DEPTH_TOPIC = f'/robot{ROBOT_ID}/oakd/stereo/image_raw'
CAMERA_INFO_TOPIC = f'/robot{ROBOT_ID}/oakd/stereo/camera_info'

NORMALIZE_DEPTH_RANGE = 3.0   # 시각화 최대 거리(m)
MAX_VALID_DEPTH = 5.0         # 유효 depth 최대 거리(m)
WINDOW_NAME = 'TurtleBot4 Depth Checker'
# ================================


class DepthChecker(Node):
    def __init__(self):
        super().__init__('depth_checker')

        self.bridge = CvBridge()
        self.K = None
        self.depth_m = None
        self.should_exit = False

        self.depth_sub = self.create_subscription(
            Image,
            DEPTH_TOPIC,
            self.depth_callback,
            qos_profile_sensor_data
        )

        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            CAMERA_INFO_TOPIC,
            self.camera_info_callback,
            qos_profile_sensor_data
        )

        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, self.mouse_callback)

        self.get_logger().info(f'Depth topic: {DEPTH_TOPIC}')
        self.get_logger().info(f'CameraInfo topic: {CAMERA_INFO_TOPIC}')
        self.get_logger().info('Press q on the OpenCV window to quit.')

    def camera_info_callback(self, msg):
        if self.K is None:
            self.K = np.array(msg.k).reshape(3, 3)

            fx = self.K[0, 0]
            fy = self.K[1, 1]
            cx = self.K[0, 2]
            cy = self.K[1, 2]

            self.get_logger().info(
                f'CameraInfo received: fx={fx:.2f}, fy={fy:.2f}, cx={cx:.2f}, cy={cy:.2f}'
            )

    def convert_depth_to_meters(self, depth_raw, encoding):
        """
        OAK-D depth image가 uint16이면 보통 mm 단위.
        float32면 보통 m 단위.
        단, 환경에 따라 다를 수 있으므로 dtype과 encoding 기준으로 처리.
        """

        depth = depth_raw.astype(np.float32)

        if encoding == '16UC1' or depth_raw.dtype == np.uint16:
            depth_m = depth / 1000.0
        elif encoding == '32FC1' or depth_raw.dtype == np.float32:
            # 대부분 m 단위지만, 값이 너무 크면 mm로 들어온 것으로 판단
            valid = depth[np.isfinite(depth) & (depth > 0)]
            if valid.size > 0 and np.nanmedian(valid) > 20.0:
                depth_m = depth / 1000.0
            else:
                depth_m = depth
        else:
            self.get_logger().warn_once(
                f'Unknown depth encoding: {encoding}, dtype={depth_raw.dtype}. Treating as millimeters.'
            )
            depth_m = depth / 1000.0

        return depth_m

    def get_roi_distance(self, x, y, radius=3):
        """
        한 픽셀만 찍으면 노이즈가 심할 수 있어서
        주변 작은 영역의 median depth를 사용.
        """

        if self.depth_m is None:
            return None

        height, width = self.depth_m.shape

        x1 = max(0, x - radius)
        x2 = min(width, x + radius + 1)
        y1 = max(0, y - radius)
        y2 = min(height, y + radius + 1)

        roi = self.depth_m[y1:y2, x1:x2]

        valid = roi[
            np.isfinite(roi) &
            (roi > 0.0) &
            (roi < MAX_VALID_DEPTH)
        ]

        if valid.size == 0:
            return None

        return float(np.median(valid))

    def depth_callback(self, msg):
        if self.should_exit:
            return

        if self.K is None:
            self.get_logger().warn('Waiting for CameraInfo...')
            return

        try:
            depth_raw = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='passthrough'
            )
        except Exception as e:
            self.get_logger().error(f'cv_bridge error: {e}')
            return

        if len(depth_raw.shape) != 2:
            self.get_logger().warn(f'Unexpected depth image shape: {depth_raw.shape}')
            return

        height, width = depth_raw.shape

        self.depth_m = self.convert_depth_to_meters(depth_raw, msg.encoding)

        cx = int(self.K[0, 2])
        cy = int(self.K[1, 2])

        center_distance = self.get_roi_distance(cx, cy)

        if center_distance is not None:
            self.get_logger().info(
                f'Image: {width}x{height}, Center ({cx}, {cy}) distance = {center_distance:.2f} m'
            )
        else:
            self.get_logger().warn(
                f'Image: {width}x{height}, Center ({cx}, {cy}) distance = invalid'
            )

        # ================================
        # 시각화
        # ================================
        depth_vis = np.nan_to_num(self.depth_m, nan=0.0, posinf=0.0, neginf=0.0)
        depth_vis = np.clip(depth_vis, 0.0, NORMALIZE_DEPTH_RANGE)
        depth_vis = (depth_vis / NORMALIZE_DEPTH_RANGE * 255.0).astype(np.uint8)

        depth_colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)

        # 중심점 표시
        cv2.circle(depth_colored, (cx, cy), 5, (0, 0, 0), -1)
        cv2.line(depth_colored, (0, cy), (width, cy), (0, 0, 0), 1)
        cv2.line(depth_colored, (cx, 0), (cx, height), (0, 0, 0), 1)

        if center_distance is not None:
            text = f'Center: {center_distance:.2f} m'
        else:
            text = 'Center: invalid'

        cv2.putText(
            depth_colored,
            text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 0),
            2
        )

        cv2.imshow(WINDOW_NAME, depth_colored)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.should_exit = True

    def mouse_callback(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        distance = self.get_roi_distance(x, y)

        if distance is None:
            self.get_logger().warn(f'Clicked ({x}, {y}) distance = invalid')
        else:
            self.get_logger().info(f'Clicked ({x}, {y}) distance = {distance:.2f} m')


def main(args=None):
    rclpy.init(args=args)
    node = DepthChecker()

    try:
        while rclpy.ok() and not node.should_exit:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()