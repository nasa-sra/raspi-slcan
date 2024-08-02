from can.interfaces import slcan
from can import Message
import can

import threading


class CANInterface:
    def __init__(
        self,
        serial_interface_name: str = "/dev/ttyUSB0",
        can_interface_name="can0",
        bitrate=500000,
    ):
        self.interface_name: str = serial_interface_name
        self.bitrate: int = bitrate
        self.jetBus: slcan.slcanBus = slcan.slcanBus(
            channel=serial_interface_name, bitrate=bitrate
        )

        self.mainBus: can.interface.Bus = can.interface.Bus(
            interface="socketcand", channel=can_interface_name
        )

    def receive_can_message(self):
        while True:
            try:
                msg: Message = self.mainBus.recv()
                self.jetBus.send(msg)
            except Exception as e:
                print(f"Jetson to Bus error: {e}")
                break

    def receive_serial_message(self):
        while True:
            try:
                msg: Message = self.jetBus.recv()
                self.mainBus.send(msg)
            except Exception as e:
                print(f"Bus to Jetson error: {e}")
                break


if __name__ == "__main__":
    can_interface: CANInterface = CANInterface(
        serial_interface_name="/dev/ttyUSB0", can_interface_name="can0", bitrate=500000
    )

    jetson_to_bus_thrd: threading.Thread = threading.Thread(
        target=can_interface.receive_serial_message
    )
    jetson_to_bus_thrd.start()
    jetson_to_bus_thrd.setDaemon(True)
    jetson_to_bus_thrd.setName("JetsonToBusThread_CAN")

    bus_to_jetson_thrd: threading.Thread = threading.Thread(
        target=can_interface.receive_can_message
    )
    bus_to_jetson_thrd.start()
    bus_to_jetson_thrd.setDaemon(True)
    bus_to_jetson_thrd.setName("BusToJetsonThread_CAN")
