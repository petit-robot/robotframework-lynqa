"""Dataset: Test run full status response."""

TEST_RUN_FULL_STATUS_SUCCESS_RESPONSE = {
    "createdAt": "2026-06-12T13:58:24.944Z",
    "start": "2026-06-12T13:58:28.693Z",
    "end": "2026-06-12T14:00:36.029Z",
    "status": "success",
    "statusMessage": "OK",
    "stepStatuses": [
        {
            "end": "2026-06-12T13:59:07.365Z",
            "start": "2026-06-12T13:58:53.483Z",
            "status": "success",
            "commands": [
                {
                    "name": "scroll",
                    "response": {"success": {"delta": 500, "direction": "down"}},
                    "screenshot": "3f85e362-d50e-4521-8447-27427110cf5f",
                },
                {
                    "name": "click",
                    "button": "left",
                    "response": {"success": {"newUrl": None}},
                    "screenshot": "4e63b6a6-b337-4642-a872-91f20a4ab919",
                    "htmlElement": '"Tout refuser button"',
                },
            ],
            "assertionsReport": {
                "assertions": [
                    {"checked": True, "assertion": "The browser is navigated to https://www.google.com/"},
                    {"checked": True, "assertion": "The Google homepage is fully loaded with the search input visible"},
                    {"checked": True, "assertion": "The cookie consent popup is dismissed"},
                ],
                "screenshot": "1be40c8c-dbb2-466e-ab1b-a5155a531fc4",
            },
        },
        {
            "end": "2026-06-12T13:59:28.493Z",
            "start": "2026-06-12T13:59:28.493Z",
            "status": "success",
            "commands": [],
            "assertionsReport": {
                "assertions": [
                    {"checked": True, "assertion": "The browser is navigated to https://www.google.com/"},
                    {
                        "checked": True,
                        "assertion": "The cookie consent popup is dismissed and the Google homepage is fully accessible",  # ruff: ignore[line-too-long]
                    },
                    {"checked": True, "assertion": "The search input is visible and accessible on the Google homepage"},
                ],
                "screenshot": "cce0c8f8-e96a-48f2-8b35-ffd41ec979dd",
            },
        },
        {
            "end": "2026-06-12T13:59:40.504Z",
            "start": "2026-06-12T13:59:40.504Z",
            "status": "success",
            "commands": [],
            "assertionsReport": {
                "assertions": [
                    {"checked": True, "assertion": "The search input exists and is visible on the Google homepage"}
                ],
                "screenshot": "296ad2a5-4cea-44a8-8af6-fbf62ce1aeaf",
            },
        },
        {
            "end": "2026-06-12T14:00:16.258Z",
            "start": "2026-06-12T14:00:00.401Z",
            "status": "success",
            "commands": [
                {
                    "name": "click",
                    "button": "left",
                    "response": {"success": {"newUrl": None}},
                    "screenshot": "62a28ce4-f106-4b70-94f7-ea640d55fcdc",
                    "htmlElement": "Search input field",
                },
                {
                    "name": "type",
                    "value": "lynqa",
                    "response": {"success": True},
                    "screenshot": "caeaa3c5-e37d-4460-a1ed-c53d81406617",
                },
                {
                    "name": "pressKey",
                    "value": "Return",
                    "response": {
                        "success": {
                            "newUrl": "https://www.google.com/search?q=lynqa&sca_esv=2aa300c80f7be1f4&source=hp&ei=gxAsaqTHMqq4kdUP1ciGmAY&iflsig=AFdpzrgAAAAAaiwek3wNXsJiALMoqmxWYThTRkSuPVDQ&ved=0ahUKEwjklP737YGVAxUqXKQEHVWkAWMQ4dUDCCE&uact=5&oq=lynqa&gs_lp=Egdnd3Mtd2l6IgVseW5xYTIMEC4YgAQYChgLGLEDMg8QLhiABBgKGAsYsQMYgwEyDBAuGAoYCxixAxiABDIMEC4YChgLGLEDGIAEMgkQLhiABBgKGAsyCRAuGIAEGAoYCzIJEAAYgAQYChgLMgkQABiABBgKGAsyCRAuGIAEGAoYCzIJEC4YgAQYChgLSJtnUMRAWJlBcAF4AJABAJgBM6AB1gGqAQE1uAEDyAEA-AEBmAIGoAKIAqgCCsICChAuGAMYjwEY6gLCAgoQABgDGI8BGOoCwgILEAAYgAQYsQMYgwHCAggQABiABBixA8ICCBAuGIAEGLEDwgIREC4YgAQYsQMYgwEYxwEY0QPCAg4QLhiABBixAxjHARjRA8ICBRAuGIAEwgIOEC4YgAQYigUYsQMYgwHCAg4QABiABBiKBRixAxiDAcICBhAAGAMYCsICBBAAGAPCAgUQABiABMICBxAAGIAEGAqYAw3xBaK8RTujFJwPkgcBNqAH50ayBwE1uAf7AcIHBTItNC4yyAcogAgB&sclient=gws-wiz&sei=3hAsauOqNoqbkdUP-YX-qAw"
                        }
                    },
                    "screenshot": "d7a51561-7ac9-4a55-bdf6-b809c5287a69",
                    "keysSequence": ["Return"],
                },
            ],
            "assertionsReport": {
                "assertions": [
                    {"checked": True, "assertion": "Search for 'lynqa' is executed and results page is displayed"},
                    {"checked": True, "assertion": "Search results include 'Smartesting' in the first results"},
                ],
                "screenshot": "3b78845d-41e8-43ba-abe2-b006e8735be2",
            },
        },
        {
            "end": "2026-06-12T14:00:35.981Z",
            "start": "2026-06-12T14:00:35.981Z",
            "status": "success",
            "commands": [],
            "assertionsReport": {
                "assertions": [
                    {"checked": True, "assertion": "The search query 'lynqa' is entered and results are displayed"},
                    {"checked": True, "assertion": "Several search results are displayed for the query 'lynqa'"},
                    {"checked": True, "assertion": "The first result displays 'Smartesting' as the source"},
                    {"checked": True, "assertion": "The first results (plural) display 'Smartesting'"},
                ],
                "screenshot": "d9b611e0-955d-4b69-a51b-58ed40d88fb3",
            },
        },
    ],
    "initialReport": {"screenshot": "b276c303-d612-4c25-a2cd-18d42b8b4930", "architecture": "omeron"},
    "type": "gherkin",
    "steps": [
        {"keyword": "Given", "text": "go to the website"},
        {"keyword": "When", "text": "I look at the search input"},
        {"keyword": "Then", "text": "the search input exists"},
        {"keyword": "When", "text": "I search for 'lynqa'"},
        {"keyword": "Then", "text": "several results are displayed and the first results display 'Smartesting'"},
    ],
}
