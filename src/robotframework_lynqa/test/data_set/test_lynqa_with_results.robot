*** Settings ***
Library     robotframework_lynqa.LynqaLibrary    api_key=%{LYNQA_API_KEY}


*** Variables ***
${LYNQA_URL}    https://www.google.com/


*** Test Cases ***
Search Engine
    Given    go to the website
    When    I look at the search input
    Then    the search input exists
    When    I search for 'lynqa'
    Then    several results are displayed and the first results display 'Smartesting'
