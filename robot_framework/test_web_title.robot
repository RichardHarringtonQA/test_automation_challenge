*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${BROWSER}    Chrome
${URL}        https://www.google.com
${EXPECTED_TITLE}    Google

*** Test Cases ***
Verify Webpage Title
    Open Browser    ${URL}    ${BROWSER}
    Title Should Be    ${EXPECTED_TITLE}
    [Teardown]    Close Browser