from can.interfaces import slcan
from can import Message
import can
import time
import threading


class CANInterface:
    def __init__(
        self,
        serial_interface_name: str = "/dev/ttyS0",
        can_interface_name="can0",
        bitrate=500000,
    ):
        self.interface_name: str = serial_interface_name
        self.bitrate: int = bitrate
        self.jetBus: slcan.slcanBus = slcan.slcanBus(
            channel=serial_interface_name
        )

        self.mainBus: can.interface.Bus = can.interface.Bus(
            interface="socketcan", channel=can_interface_name, bitrate=bitrate
        )

    def receive_can_message(self):
        while True:
            try:
                msg: Message = self.mainBus.recv()
                # print(f'Sending {msg}')
                self.jetBus.send(msg)
            except Exception as e:
                print(f"Jetson to Bus error: {e}")
                break

    def receive_serial_message(self):
        while True:
            try:
                print('Trying')
                msg: Message = self.jetBus.recv()
                print(f'Recieved {msg}')
                self.mainBus.send(msg)
            except Exception as e:
                print(f"Bus to Jetson error: {e}")
                break


if __name__ == "__main__":
    can_interface: CANInterface = CANInterface(
        serial_interface_name="/dev/ttyS0@115200", can_interface_name="can0", bitrate=500000
    )

    jetson_to_bus_thrd: threading.Thread = threading.Thread(
        target=can_interface.receive_serial_message
    )
    jetson_to_bus_thrd.daemon = True
    jetson_to_bus_thrd.name = "JetsonToBusThread_CAN"
    jetson_to_bus_thrd.start()
    print('Started jetson to bus thread')

    bus_to_jetson_thrd: threading.Thread = threading.Thread(
        target=can_interface.receive_can_message
    )
    bus_to_jetson_thrd.daemon = True
    bus_to_jetson_thrd.name = "BusToJetsonThread_CAN"
    bus_to_jetson_thrd.start()
    print('Started bus to jetson thread')

    while True:
        print("Running slcan to can adapter")
        time.sleep(1)
