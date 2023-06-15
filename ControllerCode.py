import pygame
from pygame.locals import *

import asyncio
from bleak import BleakScanner, BleakClient

async def scan():
    scanner = BleakScanner()
    devices = await scanner.discover()
    return devices

async def connect(device):
    async with BleakClient(device) as client:
        # Write a command to a characteristic by UUID
        characteristics = await client.get_services()
        pygame.init()

        # Set up the display
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Race Controller")

        clock = pygame.time.Clock()
        running = True

        # Initialize the controller
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            print("No controllers found!")
            running = False
        else:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print("Initialized controller:", joystick.get_name())

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                # Handle controller input events
                if event.type == JOYAXISMOTION:
                    axis = event.axis
                    value = event.value
                    if(axis == 0 and abs(value) > 0.1):
                        if(value < 0):
                            print(f"left{abs(value)}")
                            command = f"left{abs(value)}".encode()  # Convert command to bytes
                            await client.write_gatt_char("6E400002-B5A3-F393-E0A9-E50E24DCCA9E", command, response=True)
                            print("Command sent successfully.")
                        else:
                            print(f"right{abs(value)}")
                            command = f"righ{abs(value)}".encode()  # Convert command to bytes
                            await client.write_gatt_char("6E400002-B5A3-F393-E0A9-E50E24DCCA9E", command, response=True)
                            print("Command sent successfully.")
                        print("Axis {} moved to {:.2f}".format(axis, value))
                elif event.type == JOYBUTTONDOWN:
                    button = event.button
                    if(button == 1):
                        command = "forward".encode()  # Convert command to bytes
                        await client.write_gatt_char("6E400002-B5A3-F393-E0A9-E50E24DCCA9E", command, response=True)
                        print("Command sent successfully.")
                    if(button == 0):
                        command = "back".encode()  # Convert command to bytes
                        await client.write_gatt_char("6E400002-B5A3-F393-E0A9-E50E24DCCA9E", command, response=True)
                        print("Command sent successfully.")
                    if(button == 10):
                        command = "buzz".encode()  # Convert command to bytes
                        await client.write_gatt_char("6E400002-B5A3-F393-E0A9-E50E24DCCA9E", command, response=True)
                        print("Command sent successfully.")
                    print("Button {} pressed".format(button))
                elif event.type == JOYBUTTONUP:
                    button = event.button
                    command = "stop".encode()  # Convert command to bytes
                    await client.write_gatt_char("6E400002-B5A3-F393-E0A9-E50E24DCCA9E", command, response=True)
                    print("Command sent successfully.")

                    print("Button {} released".format(button))
                elif event.type == JOYHATMOTION:
                    hat = event.hat
                    value = event.value
                    print("Hat {} moved to {}".format(hat, value))

            # Clear the screen
            screen.fill((255, 255, 255))

            # Update the display
            pygame.display.flip()

            # Limit the frame rate
            clock.tick(60)

        # Clean up
        pygame.quit()
        

async def main():
    devices = await scan()

    # Identify and connect to your ESP32 device
    for device in devices:
        if device.address == "AD5E5B15-23F3-65B7-2841-F5A9E6009914":
            await connect(device)
            break

loop = asyncio.get_event_loop()
loop.run_until_complete(main())