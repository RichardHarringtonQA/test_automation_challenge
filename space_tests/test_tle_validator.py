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

# global failure list
failureSL = []

# log footer
def log_footer():
    run_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"\n---  END OF RUN - {run_timestamp}  ---\n")
    logger.info("\n".join(failureSL))
atexit.register(log_footer)


def validate_tle(line1, line2, testID):
    """
    setup variables
    execute each validation test
    """
    
    overall = True
    line1length = len(line1)
    line2length = len(line2)
    initial_digit = None
    calc_digit = None
    sat_num_match = None
    epoch_year = None
    epoch_day = None
    ecc_str_set = None
    satNum_slice = slice(2, 7)
    epoch_slice = slice(18, 32)
    ecc_slice = slice(26, 33)
    
    executionresult = validate_line_length(line1, line2, testID)
    overall &= executionresult
    if line1length==69: 
        executionresult, initial_digit, calc_digit  = validate_checksum(line1, testID)
        overall &= executionresult
        executionresult, sat_num_match = validate_satNum(line1, testID, satNum_slice)
        overall &= executionresult
        executionresult, epoch_year, epoch_day = validate_epoch(line1, testID, epoch_slice)
        overall &= executionresult
    if line2length==69:
        executionresult, ecc_str_set = validate_eccentricity(line2, testID, ecc_slice)
        overall &= executionresult
    executionresult = add_SQL(testID, line1length, initial_digit, calc_digit, sat_num_match, epoch_year, epoch_day, ecc_str_set)
    overall &= executionresult
    
    return overall


def validate_line_length(line1, line2, testID):
    """
    validate that each line has length == 69
    """
    
    overall = True
    
    # Check line1: length == 69
    logger.debug("Check line1: length == 69...")
    if len(line1) != 69 :
        failMSG=f"    Failed: {testID}: Line 1 length !=69"
        logger.error(failMSG) # debug output
        failureSL.append(failMSG)
        overall = False
    else:
        logger.debug("  Pass: Length = 69")
    
    # Check line2: length == 69
    logger.debug("Check line2: length == 69...")
    if len(line2) != 69 :
        failMSG=f"    Failed: {testID}: Line 2 length !=69"
        logger.error(failMSG) # debug output
        failureSL.append(failMSG)
        overall = False
    else:
        logger.debug("  Pass: Length = 69")
    
    return overall


def validate_checksum(line1, testID):
    """
    Validate checksum
    last position (68) is modulo 10 checksum value
    add all values, ignore chars, except - = 1, divide sum by 10, remainder is checksum value
    """

    overall = True

    try:
        initial_digit = int(line1[68])
        # note: this is starting at pos 68
        logger.debug(f"Expected value: {initial_digit}")
        calc_digit = sum(int(c) if c.isdigit() else (1 if c == '-' else 0) for c in line1[:68] ) % 10
        # note: this is stop at pos 68, ie up to but not including pos 68
        logger.debug(f"Calculated value: {calc_digit}")
        if initial_digit != calc_digit:
            failMSG=f"    Failed: {testID}: checksum expected {initial_digit} != calculated {calc_digit}"
            logger.error(failMSG) # debug output
            failureSL.append(failMSG)
            overall = False
        else:
            logger.debug(f"  Pass: checksum expected {initial_digit} == calculated {calc_digit}")
    except ValueError:
        failMSG=f"    Failed: {testID}: could not extract checksum digit"
        logger.error(failMSG) # debug output
        failureSL.append(failMSG)
        overall = False

    return overall, initial_digit, calc_digit


def validate_satNum(line1, testID, satNum_slice):
    """
    validate that the second token is a valid satelite number
    """
    
    overall = True

    # line 1 starts with 5-digit number after line number
    logger.debug("Check line 1 starts with 5-digit number after line number...")
    sat_num_match = line1[satNum_slice].strip()
    try:
        int(sat_num_match)
        logger.debug(f"  Pass: Sat num = {sat_num_match}")
    except ValueError:
        failMSG=f"    Failed: {testID}: could not convert {sat_num_match} to int value"
        logger.error(failMSG) # debug output
        failureSL.append(failMSG)
        overall = False
        
    return overall, sat_num_match


def validate_epoch(line1, testID, epoch_slice):
    """
    validate epoch year and day
    """
    
    overall = True
    
    # Validate Epoch Year and Day
    logger.debug("Check Line 1 epoch year and day...")
    epoch = line1[epoch_slice].strip()
    logger.debug(f"Epoch is: {epoch}")
    # 2 digit year followed by 3 digit day increment with partial day decimal
    epoch_year = int(epoch[:2])
    if epoch_year > 56 or epoch_year < 26:
        logger.debug(f"  Pass: valid epoch year: {epoch_year}")
    else:
        failMSG=f"    Failed: {testID}: invalid epoch year: {epoch_year}"
        logger.error(failMSG) # debug output
        failureSL.append(failMSG)
        overall = False
    epoch_day = int(epoch[2:5])
    if epoch_day > 0 and epoch_day < 357:
        logger.debug(f"  Pass: valid epoch day: {epoch_day}")
    else:
        failMSG=f"    Failed: {testID}: invalid epoch day: {epoch_day}"
        logger.error(failMSG) # debug output
        failureSL.append(failMSG)
        overall = False
        
    return overall, epoch_year, epoch_day


def validate_eccentricity(line2, testID, ecc_slice):
    """
    validate line 2 eccentricity value is an int
    as leading decimal is implied
    thus a valid int == valid < 1 value
    """

    overall = True
    
    logger.debug("Check line2: eccentricity (5th token) < 1.0")
    # extract fixed position value
    ecc_str_set = line2[ecc_slice].strip()
    # note this is a string capture, must make it number for comparison purposes
    try:
        ecc_val = float(ecc_str_set) # string to number
        ecc_int = int(ecc_val)
        #check number is whole 
        if ecc_val == ecc_int:
            logger.debug(f"  Pass: Eccentricity {ecc_val} < 1")
        else:
            failMSG=f"    Failed: {testID}: Eccentricity {ecc_val} is invalid"
            logger.error(failMSG) # debug output
            failureSL.append(failMSG)
            overall = False
    except ValueError:
        failMSG=f"    Failed: {testID}: could not convert eccentricity extracted string to float value"
        logger.error(failMSG) # debug output
        failureSL.append(failMSG)
        overall = False
        
    return overall, ecc_str_set
    

def add_SQL(line1length, initial_digit, calc_digit, sat_num_match, epoch_year, epoch_day, ecc_str_set, testID):
    """
    practice creating / populating / extracting from / displaying data from a SQL DB
    """
    
    overall = True
    
    # make a temp SQL table
    with sqlite3.connect(':memory:') as myDB:
        myDB.execute('CREATE TABLE TLE_Values (line1length int, line1checkSumVal int, line1checkSumCalc int, satNum TEXT, epochYr int, epochDay int, line2Ecc TEXT)')
        # insert extracted values
        try:
            myDB.execute('INSERT INTO TLE_Values (line1length, line1checkSumVal, line1checkSumCalc, satNum, epochYr, epochDay, line2Ecc) VALUES (?, ?, ?, ?, ?, ?, ?)', (line1length, initial_digit, calc_digit, sat_num_match, epoch_year, epoch_day, ecc_str_set))
            # output table values
            tempTable = myDB.execute('SELECT * FROM TLE_Values;')
            result = tempTable.fetchall()
        except sqlite3.Error as e:
            failMSG=f"    Failed: {testID}: could not write to SQL table: {str(e)}"
            logger.error(failMSG) # debug output
            failureSL.append(failMSG)
            overall = False            
        logger.debug(f"SQL result: {result}")
    
    return overall


class TestTLEValidator(unittest.TestCase):
    def test_valid_tle(self):
        logger.debug("***test1***")
        line1 = "1 00011U 59001A   25266.56989994  .00000842  00000-0  43621-3 0  9990"   # Valid line1
        line2 = "2 00011  32.8735  13.8888 1448157 340.0672  14.8534 11.90033149503789"   # Valid line2
        self.assertTrue(validate_tle(line1, line2, "Test1"))

    def test_invalid_ecc(self):
        logger.debug("***test2***")
        line1 = "1 25544U 98067A   25268.12345678  .00002182  00000-0  12345-4 0  9999"
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"   # Modified ecc >1
        line2 = line2.replace("0001234", "2.1234567")  # Invalid ecc = 2.12
        self.assertFalse(validate_tle(line1, line2, "Test2"))

    def test_invalid_line1(self):
        logger.debug("***test3***")
        line1 = "Invalid line1"   # Too short
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"
        self.assertFalse(validate_tle(line1, line2, "Test3"))

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