#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from irobot_create_msgs.msg import AudioNote, AudioNoteVector
from builtin_interfaces.msg import Duration


class AudioPublisher(Node):

    def __init__(self):
        super().__init__('audio_publisher')

        self.publisher = self.create_publisher(
            AudioNoteVector,
            '/robot1/cmd_audio',  # 필요시 robot 번호 변경
            10
        )

        # 노드 시작 후 1초 뒤 한 번만 실행
        self.timer = self.create_timer(1.0, self.publish_audio)

        self.sent = False

    def create_note(self, frequency, nanosec):
        note = AudioNote()
        note.frequency = float(frequency)

        duration = Duration()
        duration.sec = 0
        duration.nanosec = nanosec

        note.max_runtime = duration
        return note

    def publish_audio(self):

        if self.sent:
            return

        msg = AudioNoteVector()
        msg.append = False

        msg.notes = [
            self.create_note(880.0, 300000000),  # 삐
            self.create_note(440.0, 300000000),  # 뽀
            self.create_note(880.0, 300000000),  # 삐
            self.create_note(440.0, 300000000),  # 뽀
        ]

        self.publisher.publish(msg)

        self.get_logger().info('Audio sequence published!')

        self.sent = True

        # 한 번만 실행하고 종료
        self.destroy_timer(self.timer)
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    node = AudioPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()


if __name__ == '__main__':
    main()