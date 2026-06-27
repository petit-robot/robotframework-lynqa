*** Settings ***
Documentation       Acceptance test executed against the real Lynqa service.
...                 Requires the ``LYNQA_API_KEY`` environment variable to be set to a valid Lynqa API key.
...                 Runs a Google search for "lynqa" and checks that the first result mentions "Smartesting".

Library             robotframework_lynqa.LynqaLibrary    api_key=%{LYNQA_API_KEY}


*** Variables ***
${LYNQA_URL}        https://www.google.com/


*** Test Cases ***
Search Engine
    Given    go to the website
    When    I look at the search input
    Then    the search input exists
    When    I search for 'lynqa'
    Then    several results are displayed and the first results display 'Smartesting'
