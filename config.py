##### plotting settings

SHAPE_COLOR = 'black'
BRIDGE_COLOR = 'red'
START_DOT_COLOR = 'green'
END_DOT_COLOR = 'blue'
DOMAIN_COLOR = 'grey'
PLOTTING_RESOLUTION = 2
PLOT_THICKNESS = 1
START_END_DOT_SIZE = 7
PLOT_XLIM = [-80, 80]
PLOT_YLIM = [55, 175]

DOMAIN_BOX = [[-70, 70], [-70, 120], [70, 120], [70, 70]] # Points: botttom left, top left, top right, bottom right
DOMAIN_DOME = [[-70, 120], [70, 120], 80, -1] # Start point, end point, radius, direction of a partial circle

##### Other settings

SERIAL_DELAY = 0.005 #seconds
BAUD = 115200
WRITE_TIMEOUT = 0.5
USB_ID = '/dev/ttyUSB0'  #