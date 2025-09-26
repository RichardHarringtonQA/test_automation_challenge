# Test Automation Challenge

This repository contains a beginner-level test automation project to demonstrate skills in Robot Framework, Python, and Postman for web and API testing. The project was created to prepare for a Test Automation Engineer role, focusing on scripting and testing frameworks.

## Project Overview
- **Web Test**: A Robot Framework test using SeleniumLibrary to verify the title of a webpage (https://www.example.com).
- **API Test**: A Postman collection to test a public API endpoint (https://jsonplaceholder.typicode.com/posts/1).
- **Python Unit Test Scripting**: A set of Python unit tests to validate simulated TLE data inputs.

## Prerequisites
- Python 3.x
- Robot Framework (`pip install robotframework`)
- SeleniumLibrary (`pip install robotframework-seleniumlibrary`)
- Chrome browser and ChromeDriver
- Postman (for API test)

## Setup
1. Clone the repository: `git clone https://github.com/yourusername/test-automation-challenge.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure ChromeDriver is in your system PATH or project folder.

## Running the Tests
- **Web Test**: Run `robot robot_tests/test_web_title.robot`
- **API Test**: Import `postman/api_test_challenge.postman_collection.json` into Postman and send the request.
- **Py Unit Test**: Run `py robot_framework\space_tests\test_tle_validator.py`

## Results
- Web test results are saved in `output.xml` and `report.html`.
- API test results are visible in Postman’s Test Results tab.
- Py Unit Test results output in console (#upgrade to logging for permanence)

## Purpose
This project showcases my learning in test automation, leveraging my QA experience with Selenium and Postman to build skills in Python and Robot Framework for a Test Automation Engineer role.

## Contact
Richard Harrington | rahpost@gmail.com
