
from SF000_Lidar import SF000_Lidar
sfLidar = SF000_Lidar('/dev/ttyUSB0', 115200)


sfLidar.request_product_name()
sfLidar.request_hardware_version()
sfLidar.request_firmware_version()
sfLidar.request_serial_number()

sfLidar.request_stream()



