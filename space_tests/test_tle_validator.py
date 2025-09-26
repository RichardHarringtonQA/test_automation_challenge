import unittest
import re
import logging
import time
import atexit

"""
cleanse log file (optional)
echo. > test_log.log
execute via:
py -3 -m unittest test_tle_validator -v
python launcher : version 3.x modern features : run module as script : module name : dot path package/directory.test_file_name : verbose test name and result status output
"""

# configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('test_log.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
# NOTE: log file will be created in execution folder

# log header
run_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
logger.info(f"---  START OF RUN - {run_timestamp}  ---")

# log footer
def log_footer():
    run_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"---  END OF RUN - {run_timestamp}  ---\n")
atexit.register(log_footer)


def validate_tle(line1, line2):
    logger.debug("Check line1: length == 69...")
    if len(line1) != 69 :
        logger.error("  Failed: Line 1 length !=69") # debug output
        return False
    else:
        logger.debug("  Pass: Length = 69")
    
    logger.debug("Check line 1 starts with 5-digit number after line number...")
    # using flexible token matching, not strictly ideal, but good practice
    sat_num_match = re.search(r"^.+?\s+(\d{5})", line1)
    # logger.debug(sat_num_match) # debug regex match
    if sat_num_match:
        sat_num = sat_num_match.group(1) # extract 5 digit number
        logger.debug(f"  Pass: Sat num = {sat_num}")
    else :
        logger.error("  Failed: Second token invalid sat num.") # debug output
        return False
    
    logger.debug("Check line2: eccentricity (5th token) < 1.0")
    """
    # flexible token extraction
    # may not be ideal solution as tokens are expected to be at fixed positions within given strings
    # extract the 5th token
    ecc_str = re.search(r"^.+?\s+.+?\s+.+?\s+.+?\s+(.+?)\s", line2)
    logger.debug(ecc_str) # the whole capture
    logger.debug(ecc_str.group(1)) # only the target group capture
    """
    # extract fixed position value
    ecc_str_set = line2[26:33].strip()
    # debug    logger.debug (f"extracted val: {ecc_str_set}") # debug fixed length capture
    # note this is a string capture, must make it number for comparison purposes
    try:
        ecc_val = float(ecc_str_set) # string to number
        # debug        logger.debug(f"float val: {ecc_val}")
        ecc_int = int(ecc_val)
        # debug        logger.debug(f"int val: {ecc_int}")
        #check number is whole 
        if ecc_val == ecc_int:
            logger.debug(f"  Pass: Eccentricity {ecc_val} < 1")
        else:
            logger.error(f"  Failed: Eccentricity {ecc_val} is invalid")
            return False
    except ValueError:
        logger.error("  Failed: could not convert extracted string to float value")
        return False

    
class TestTLEValidator(unittest.TestCase):
    def test_valid_tle(self):
        logger.debug("***test1***")
        line1 = "1 25544U 98067A   25268.12345678  .00002182  00000-0  12345-4 0  9999"   # Mock valid line1
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"   # Mock valid line2 (ecc ~0.0001234)
        self.assertTrue(validate_tle(line1, line2))

    def test_invalid_ecc(self):
        logger.debug("***test2***")
        line1 = "1 25544U 98067A   25268.12345678  .00002182  00000-0  12345-4 0  9999"
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"   # Modified ecc >1
        line2 = line2.replace("0001234", "2.1234567")  # Invalid ecc = 2.12
        self.assertFalse(validate_tle(line1, line2))

    def test_invalid_line1(self):
        logger.debug("***test3***")
        line1 = "Invalid line1"   # Too short
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"
        self.assertFalse(validate_tle(line1, line2))

if __name__ == '__main__':
    unittest.main()