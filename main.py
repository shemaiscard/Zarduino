from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.clock import Clock
import bluetooth  # Make sure pybluez is available on your build system

class BluetoothCarController(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.socket = None
        self.device_address = None

        # Connect/Disconnect Button
        self.connect_btn = Button(text="Connect Bluetooth", size_hint=(1, 0.1))
        self.connect_btn.bind(on_press=self.toggle_connection)
        self.add_widget(self.connect_btn)

        # Speed Slider
        self.speed_label = Label(text="Speed: 0%", size_hint=(1, 0.1))
        self.speed_slider = Slider(min=0, max=100, value=0, size_hint=(1, 0.1))
        self.speed_slider.bind(value=self.on_speed_change)
        self.add_widget(self.speed_label)
        self.add_widget(self.speed_slider)

        # Directional Buttons
        controls_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.7))

        # Forward button
        forward_btn = Button(text="Forward", size_hint=(1, 0.33))
        forward_btn.bind(on_press=lambda x: self.send_command("F"))
        controls_layout.add_widget(forward_btn)

        # Left, Stop, Right buttons
        middle_controls = BoxLayout(size_hint=(1, 0.33))
        left_btn = Button(text="Left")
        left_btn.bind(on_press=lambda x: self.send_command("L"))
        stop_btn = Button(text="Stop")
        stop_btn.bind(on_press=lambda x: self.send_command("S"))
        right_btn = Button(text="Right")
        right_btn.bind(on_press=lambda x: self.send_command("R"))
        middle_controls.add_widget(left_btn)
        middle_controls.add_widget(stop_btn)
        middle_controls.add_widget(right_btn)
        controls_layout.add_widget(middle_controls)

        # Backward button
        backward_btn = Button(text="Backward", size_hint=(1, 0.33))
        backward_btn.bind(on_press=lambda x: self.send_command("B"))
        controls_layout.add_widget(backward_btn)

        self.add_widget(controls_layout)

    def toggle_connection(self, instance):
        if self.socket:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        try:
            self.device_address = self.find_hc06()
            if self.device_address:
                self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.socket.connect((self.device_address, 1))
                self.connect_btn.text = "Disconnect Bluetooth"
        except Exception as e:
            self.connect_btn.text = f"Connection Failed"

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            self.connect_btn.text = "Connect Bluetooth"

    def find_hc06(self):
        nearby_devices = bluetooth.discover_devices(duration=5, lookup_names=True)
        for addr, name in nearby_devices:
            if "HC-06" in name.upper():
                return addr
        return None

    def send_command(self, command):
        if self.socket:
            try:
                self.socket.send(command)
            except:
                self.disconnect()

    def on_speed_change(self, instance, value):
        self.speed_label.text = f"Speed: {int(value)}%"
        self.send_command(f"SPEED:{int(value)}")  # Assumes car firmware handles this

class CarApp(App):
    def build(self):
        return BluetoothCarController()

if __name__ == '__main__':
    CarApp().run()
