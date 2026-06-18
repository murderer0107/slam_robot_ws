import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from irobot_create_msgs.msg import AudioNote
from irobot_create_msgs.msg import AudioNoteVector


class BeepNode(Node):

    def __init__(self):
        super().__init__('beep_node')

        # TurtleBot4 robot8의 오디오 명령 토픽
        self.topic_name = '/robot8/cmd_audio'

        # Create3 / TurtleBot4 cmd_audio는 Reliable QoS를 쓰는 게 안전함
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE
        )

        # AudioNoteVector 메시지를 /robot8/cmd_audio로 publish할 publisher 생성
        self.publisher_ = self.create_publisher(
            AudioNoteVector,
            self.topic_name,
            qos_profile
        )

        # 한 번만 실행하고 종료하기 위한 플래그
        self.done = False

        # ROS2 discovery 시간을 조금 주기 위해 1초 뒤에 소리 publish
        self.timer = self.create_timer(1.0, self.play_sound)

        self.get_logger().info(f'Beep node started. topic: {self.topic_name}')

    def make_note(self, frequency, nanosec=300_000_000):
        # AudioNote 메시지 하나 생성
        note = AudioNote()

        # 주파수 설정
        # 880Hz = 높은 삐, 440Hz = 낮은 뽀
        note.frequency = int(frequency)

        # 음 길이 설정
        note.max_runtime.sec = 0
        note.max_runtime.nanosec = nanosec

        return note

    def play_sound(self):
        # AudioNoteVector 메시지 생성
        msg = AudioNoteVector()

        # false면 기존 재생 목록에 이어붙이지 않고 새로 재생
        msg.append = False

        # 삐-뽀-삐-뽀 패턴
        msg.notes = [
            self.make_note(880),  # 삐
            self.make_note(440),  # 뽀
            self.make_note(880),  # 삐
            self.make_note(440),  # 뽀
        ]

        # 메시지 publish
        self.publisher_.publish(msg)

        self.get_logger().info('Published beep-boop sound to TurtleBot4.')

        # 한 번 publish 후 종료 준비
        self.done = True
        self.destroy_timer(self.timer)


def main(args=None):
    rclpy.init(args=args)

    node = BeepNode()

    try:
        # done이 True가 될 때까지 노드 실행
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
