import unittest
import re

def validate_tle(line1, line2):
    """
    Original function: Validate TLE data.
    - line1: Starts with satellite number (5 digits), after line number.
    - line2: Eccentricity < 1.0 (valid orbit).
    Returns True if valid, False otherwise.
    """
    
    print("Check line1: length == 69...")
    if len(line1) != 69 :
        print("  Failed: Line 1 length !=69") # debug output
        return False
    else:
        print("  Pass: Length = 69")
    
    print("Check line 1 starts with 5-digit number after line number...")
    # using flexible token matching, not strictly ideal, but good practice
    sat_num_match = re.search(r"^.+?\s+(\d{5})", line1)
    # print(sat_num_match) # debug regex match
    if sat_num_match:
        sat_num = sat_num_match.group(1) # extract 5 digit number
        print(f"  Pass: Sat num = {sat_num}")
    else :
        print("  Failed: Second token invalid sat num.") # debug output
        return False
    
    print("Check line2: eccentricity (5th token) < 1.0")
    """
    flexible token extraction
    may not be ideal solution as tokens are expedted to be fixed positions within given strings
    # extract the 5th token
    ecc_str = re.search(r"^.+?\s+.+?\s+.+?\s+.+?\s+(.+?)\s", line2)
    print(ecc_str) # the whole capture
    print(ecc_str.group(1)) # only the target group capture
    """
    # extract fixed position value
    ecc_str_set = line2[26:33].strip()
    # debug    print (f"extracted val: {ecc_str_set}") # print fixed length capture
    # note this is a string capture, must make it number for comparison purposes
    try:
        ecc_val = float(ecc_str_set) # string to number
        # debug        print(f"float val: {ecc_val}")
        ecc_int = int(ecc_val)
        # debug        print(f"int val: {ecc_int}")
        #check number is whole 
        if ecc_val == ecc_int:
            print(f"  Pass: Eccentricity {ecc_val} < 1")
        else:
            print(f"  Failed: Eccentricity {ecc_val} is invalid")
            return False
    except ValueError:
        print("  Failed: could not convert extracted string to float value")
        return False
    
    
class TestTLEValidator(unittest.TestCase):
    def test_valid_tle(self):
        print("***test1***")
        line1 = "1 25544U 98067A   25268.12345678  .00002182  00000-0  12345-4 0  9999"   # Mock valid line1
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"   # Mock valid line2 (ecc ~0.0001234)
        self.assertTrue(validate_tle(line1, line2))

    def test_invalid_ecc(self):
        print("***test2***")
        line1 = "1 25544U 98067A   25268.12345678  .00002182  00000-0  12345-4 0  9999"
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"   # Modified ecc >1
        line2 = line2.replace("0001234", "2.1234567")  # Invalid ecc = 2.12
        self.assertFalse(validate_tle(line1, line2))

    def test_invalid_line1(self):
        print("***test3***")
        line1 = "Invalid line1"   # Too short
        line2 = "2 25544  51.6456 123.4567 0001234 123.4567 234.5678 15.12345678123456"
        self.assertFalse(validate_tle(line1, line2))

if __name__ == '__main__':
    unittest.main()