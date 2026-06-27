*** Settings ***
Library     robotframework_lynqa.LynqaLibrary    api_key=%{LYNQA_API_KEY}


*** Variables ***
${LYNQA_URL}            https://www.super-u.ai
${LYNQA_LANGUAGE}       rf-RF
&{LYNQA_SECRETS}        login=superu    password=TrèsS3cr3t


*** Test Cases ***
Browsing And Buying An AI Agent
    Given    the storefront is open at the home page
    When    the user searches for an autonomous testing agent
    When    the user filters the results to top-rated agents under 50 credits
    Then    a list of matching AI agents is displayed with their prices
    Then    the premium "Bobcat" agent is sold out because its success
