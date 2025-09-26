import unittest
import re
import logging
import time
import atexit
import sqlite3

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
    # Check line1: length == 69
    logger.debug("Check line1: length == 69...")
    if len(line1) != 69 :
        logger.error("  Failed: Line 1 length !=69") # debug output
        return False
    else:
        line1length = 69
        logger.debug("  Pass: Length = 69")
    # Validate checksum
    # last position (68) is modulo 10 checksum value
    # add all values, ignore chars, except - = 1, divide sum by 10, remainder is checksum value
    initial_digit = int(line1[68])
    # note: this is starting at pos 68
    logger.debug(f"Expected value: {initial_digit}")
    calc_digit = sum(int(c) if c.isdigit() else (1 if c == '-' else 0) for c in line1[:68] ) % 10
    # note: this is stop at pos 68, ie up to but not including pos 68
    logger.debug(f"Calculated value: {calc_digit}")
    if initial_digit != calc_digit:
        logger.debug(f"  Fail: checksum expected {initial_digit} != calculated {calc_digit}")
        return False
    else:
        logger.debug(f"  Pass: checksum expected {initial_digit} == calculated {calc_digit}")
    
    # line 1 starts with 5-digit number after line number
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
        
    # Validate Epoch Year and Day
    logger.debug("Check Line 1 epoch year and day...")
    # position 18-32
    epoch = line1[18:32].strip()
    # debug
    logger.debug(epoch)
    # 2 digit year followed by 3 digit day increment with partial day decimal
    epoch_year = int(epoch[:2])
    if epoch_year > 56 or epoch_year < 26:
        logger.debug(f"  Pass: valid epoch year {epoch_year}")
    else:
        logger.debug(f"  Fail: invalid epoch year {epoch_year}")
        return False
    epoch_day = int(epoch[2:5])
    if epoch_day > 0 and epoch_day < 357:
        logger.debug(f"  Pass: valid epoch day {epoch_day}")
    else:
        logger.debug(f"  Fail: invalid epoch day {epoch_day}")
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
        
    # make a temp SQL table
    with sqlite3.connect(':memory:') as myDB:
        myDB.execute('CREATE TABLE TLE_Values (line1length int, line1checkSumVal int, line1checkSumCalc int, satNum TEXT, epochYr int, epochDay int, line2Ecc TEXT)')
        # insert extracted values
        myDB.execute('INSERT INTO TLE_Values (line1length, line1checkSumVal, line1checkSumCalc, satNum, epochYr, epochDay, line2Ecc) VALUES (?, ?, ?, ?, ?, ?, ?)', (line1length, initial_digit, calc_digit, sat_num, epoch_year, epoch_day, ecc_str_set))
        # output table values
        cursor = myDB.execute('SELECT * FROM TLE_Values;')
        result = cursor.fetchall()
        logger.debug(f"SQL result: {result}")
        return bool(result)

    
class TestTLEValidator(unittest.TestCase):
    def test_valid_tle(self):
        logger.debug("***test1***")
        line1 = "1 00011U 59001A   25266.56989994  .00000842  00000-0  43621-3 0  9990"   # Valid line1
        line2 = "2 00011  32.8735  13.8888 1448157 340.0672  14.8534 11.90033149503789"   # Valid line2
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

"""
actual valid examples:
1 00011U 59001A   25266.56989994  .00000842  00000-0  43621-3 0  9990
2 00011  32.8735  13.8888 1448157 340.0672  14.8534 11.90033149503789
1 00011U 59001A   25267.32543098  .00000877  00000-0  45568-3 0  9996
2 00011  32.8730  11.0311 1448100 344.3649  11.6378 11.90034338503786
1 00012U 59001B   25266.88333266  .00003689  00000-0  21793-2 0  9998
2 00012  32.8956  83.5955 1647154 135.1432 239.4715 11.48010322500705
"""


if __name__ == '__main__':
    unittest.main()