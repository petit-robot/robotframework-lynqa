*** Settings ***
Library     DateTime
Library     robotframework_lynqa.LynqaLibrary    api_key=%{API_KEY}


*** Variables ***
${LYNQA_LANGUAGE}       rf-RF
${LYNQA_DATETIME}       Wed May 8 2026 09:00:00 GMT+0200
&{LYNQA_SECRETS}        login=superu    password=TrèsS3cr3t


*** Test Cases ***
Browsing And Buying An AI Agent Without URL
    Given    the storefront is open at the home page
    When    the user searches for an autonomous testing agent
    Then    a list of matching AI agents is displayed with their prices
