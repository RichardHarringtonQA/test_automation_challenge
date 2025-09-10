*** Settings ***
Library     SeleniumLibrary
Library     c:/automation_challenge/robot_framework/search_utils.py

*** Variables ***
${BROWSER}          Chrome
${URL}              https://www.ask.com
${SEARCH_TERM}      Test Automation

${SEARCH_INPUT}     css=input[aria-label='Search']		
# updated locator based on element inspection, note must use css or xpath for aria-label locator as not natively supported by selenium

${EXPECTED_TITLE}   ${SEARCH_TERM}, ${URL}

*** Test Cases ***
Verify Search Form Submission
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window		# simulates real user behavior
    Page Should Contain Element    ${SEARCH_INPUT}    timeout=5s		# Verify locator
    Log    Locator ${SEARCH_INPUT} found successfully		# log locator status
    Input Text      ${SEARCH_INPUT}    ${SEARCH_TERM}
    Press Keys      ${SEARCH_INPUT}    ENTER
    Wait Until Page Contains    ${SEARCH_TERM}    timeout=10s		# with timeout failsafe
    # get the current title for later parsing
	${current_title}=    Get Title		
    Log    Actual title: ${current_title}		# Debug title

	#	Should Contain	${current_title}	${SEARCH_TERM}		
	# ‘should contain’ is flexible thus more robust than ‘title should be’ which is exact
	
	Verify Search Results   ${SEARCH_TERM}        #	custom keyword search util
    #note needs a full tab of white space, a single space is insufficient
	
    [Teardown]	Close Browser