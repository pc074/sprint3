# Example of interaction with a BLE UART device using a UART service
# implementation.
# Author: Tony DiCola
import sys
import thread
import Adafruit_BluefruitLE
import atexit
import time
from Adafruit_BluefruitLE.services import UART
import multiprocessing

DEVICE_NAME = "Adafruit Bluefruit LE"
ARGS_1 = []
ARGS_2 = []


# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

def foward_taps(uart_1, uart_2, device_1, device_2, max_timeout):
  timeouts = 0
  while True:
    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
      # Now wait up to one minute to receive data from the device.
      print('Waiting up to 60 seconds to receive data from device {}'.format(device_1.id))
      received = uart_1.read(timeout_sec=60)
      if received is not None:
          # Received data, print it out.
          uart_2.write('tap\r\n')
          print("Sent tap from {} to {}".format(device_1.id, device_2.id))
      else:
          # Timeout waiting for data, None is returned.
          print('1 timeout')
          timeouts += 1
          if timeouts >= max_timeout:
            return
    except:
      print "Communication failure in fowarder {} --> {}\n".format(device_1.id, device_2.id)
      return


# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def main():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    # Scan for UART devices.
    print('Searching for UART device...')
    num_devices = 2

    # Start scanning with the bluetooth adapter.
    adapter.start_scan()
    # Use atexit.register to call the adapter stop_scan function before quiting.
    # This is good practice for calling cleanup code in this main function as
    # a try/finally block might not be called since this is a background thread.
    atexit.register(adapter.stop_scan)
    # Enter a loop and print out whenever a new UART device is found.
    adafruit_devices = []
    known_uarts = set()
    for i in range(100):
        # Call UART.find_devices to get a list of any UART devices that
        # have been found.  This call will quickly return results and does
        # not wait for devices to appear.
        found = set(UART.find_devices())
        # Check for new devices that haven't been seen yet and print out
        # their name and ID (MAC address on Linux, GUID on OSX).
        new = found - known_uarts
        for device in new:
            if device.name == DEVICE_NAME:
              adafruit_devices.append(device)
              print('Found UART: {0} [{1}]'.format(device.name, device.id))
        known_uarts.update(new)
        # Sleep for a second and see if new devices have appeared.
        time.sleep(0.5)
        if len(adafruit_devices) >= num_devices:
            break
    adapter.stop_scan()

    if len(adafruit_devices) < num_devices:
      print("could not find 2 devices")
      sys.exit(1)

    print('Connecting to device...')
    device_1 = adafruit_devices[0]
    device_1.connect()  
    atexit.register(device_1.disconnect)
    device_2 = adafruit_devices[1]
    device_2.connect()
    atexit.register(device_2.disconnect)
    com_fail = False

    try:
      # Wait for service discovery to complete for the UART service.  Will
      # time out after 60 seconds (specify timeout_sec parameter to override).
      print('Discovering services...')
      UART.discover(device_1)
      UART.discover(device_2)

      # Once service discovery is complete create an instance of the service
      # and start interacting with it.
      uart_1 = UART(device_1)
      uart_2 = UART(device_2)
    except:
      com_fail = True

    if not com_fail:
      print("calling foward_taps")
      thread.start_new_thread( foward_taps, (uart_1, uart_2, device_1, device_2, 5, ))
      time.sleep(1)
      thread.start_new_thread( foward_taps, (uart_2, uart_1, device_2, device_1, 5, ))
      while True:
        pass

# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)