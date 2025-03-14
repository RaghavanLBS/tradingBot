# importing module
import logging,datetime
from pathlib import Path



# Create and configure logger

todayLogFile = f"logs\\newfile{datetime.datetime.today().strftime('%Y-%m-%d')}.log"
my_file = Path(todayLogFile)
if my_file.is_file() == True:
    logging.basicConfig(filename=todayLogFile,
                format='%(asctime)s %(message)s',
                filemode='a')
else:
    logging.basicConfig(filename=todayLogFile,
                format='%(asctime)s %(message)s',
                filemode='w')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

def info(message):
    logger.info(message)
def error(message):
    logger.error(message)