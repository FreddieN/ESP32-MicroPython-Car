
from machine import Pin, Timer, SoftI2C, PWM
from time import sleep_ms
import ubluetooth
import time

a1 = PWM(Pin(5), freq = 1000)
a2 = PWM(Pin(17), freq = 1000)
b1 = PWM(Pin(16), freq = 1000)
b2 = PWM(Pin(4), freq = 1000)
a1.duty(0)
a2.duty(0)
b1.duty(0)
b2.duty(0)

class BLE():
    def __init__(self, name):
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)

# Change the pin from 2 to 25 to flash the white on-board LED while connected (using it below for another reason).
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        self.timer2 = Timer(1)

        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.timer1.deinit()
        self.timer2.deinit()

    def disconnected(self):
        self.timer1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: self.led(1))
        sleep_ms(200)
        self.timer2.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: self.led(0))

    def ble_irq(self, event, data):
        if event == 1:
            '''Central disconnected'''
            self.connected()
            self.led(1)

        elif event == 2:
            '''Central disconnected'''
            self.advertiser()
            self.disconnected()

        elif event == 3:
            '''New message received'''
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode('UTF-8').strip()
            print(message)
            print(message[:4])
            if message[:4] == 'left':
                print(message[4:])
                power = int(1023*float(message[4:7]))
                print(power)
                a1.duty(0)
                a2.duty(power)
                b1.duty(0)
                b2.duty(0)
            if message[:4] == 'righ':
                print(message[4:])
                power = int(1023*float(message[4:7]))
                print(power)
                a1.duty(0)
                a2.duty(0)
                b1.duty(0)
                b2.duty(power)
            if message == 'forward':
                a1.duty(1023)
                a2.duty(0)
                b1.duty(1023)
                b2.duty(0)
            if message == 'back':
                a1.duty(0)
                a2.duty(1023)
                b1.duty(0)
                b2.duty(1023)
            if message == 'stop':
                a1.duty(0)
                a2.duty(0)
                b1.duty(0)
                b2.duty(0)
                print('stop')
            if message == 'led':
                led.value(not led.value())
                print('led', led.value())
                ble.send('led' + str(led.value()))

    def register(self):
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)

        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        self.ble.gap_advertise(100, bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name)

def stop():
    a1.duty(0)
    a2.duty(0)
    b1.duty(0)
    b2.duty(0)
# test
led = Pin(25, Pin.OUT)
# You should change this line of code to name your own ESP32 - otherwise, chaos! :)
ble = BLE("Freddie's ESP32")
