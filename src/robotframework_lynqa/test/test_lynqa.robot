*** Settings ***
Library     robotframework_lynqa.LynqaLibrary    api_key=%{API_KEY}


*** Variables ***
${URL}          https://www.agent-u.ai/


*** Tasks ***
Browsing And Buying An AI Agent

    Given    the AgentU storefront is open at the home page
    When     the user searches for an autonomous testing agent
    And      the user filters the results to top-rated agents under 50 credits
    Then     a list of matching AI agents is displayed with their prices
    But      the premium "Bobcat" agent is sold out because its success
