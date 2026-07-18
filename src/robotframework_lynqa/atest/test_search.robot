*** Settings ***
Documentation       Acceptance test executed against the real Lynqa service.
...                 Requires the ``LYNQA_API_KEY`` environment variable to be set to a valid Lynqa API key.

Library             robotframework_lynqa.LynqaLibrary    api_key=%{LYNQA_API_KEY}


*** Variables ***
${LYNQA_URL}    https://practice.expandtesting.com/


*** Test Cases ***
Search Engine
    Given    go to the website
    When    I look at the search input
    Then    the search input exists
    When    I search for 'login'
    Then    several results are filtered
    Then    the first result concerns 'Page Login'
    When    I try out 'Page Login'
    Then    The page allows to test a login
