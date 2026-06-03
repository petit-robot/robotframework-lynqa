"""Data set for test purpose."""

TEST_RUN_ID = "mf4zz9945nwbofv81shozwb5"
TEST_RUN_ID_2 = "zcuk4l13zax1piz2h73imct6"

TEST_RUN = {
    "url": "https://example.com/",
    "name": "My test name",
    "context": {
        "clientLanguage": "en-US, english, en",
        "clientDatetime": "Thu Feb 26 2026 09:26:12 GMT+0100 (Central Europe time)",
        "secrets": [{"name": "password", "value": "mys4cr4t!"}],
    },
    "guidance": [{"text": "The user is between 18 and 49"}],
    "attachments": [{"name": "invoice_260313.pdf", "id": "string"}],
    "type": "manual",
    "steps": [
        {
            "action": 'Click on the "Login" button',
            "expectedResult": "Verify that the user is logged-in",
            "guidance": [{"text": "The user is between 18 and 49"}],
            "attachments": [{"name": "invoice_260313.pdf", "id": "string"}],
        }
    ],
}

TEST_RUN_STATUS = {
    "initialReport": {"screenshot": "4b111ba4-c236-4770-67bf-0f17d0230e47"},
    "status": "running",
    "statusMessage": "Insufficient credits",
    "start": "2025-09-18T09:00:00.000Z",
    "end": "2025-09-18T09:05:27.000Z",
    "expiration": "2025-09-18T09:05:27.000Z",
}

TEST_RUN_FULL_STATUS = {
    "initialReport": {"screenshot": "4b111ba4-c236-4770-67bf-0f17d0230e47"},
    "status": "running",
    "statusMessage": "Insufficient credits",
    "start": "2025-09-18T09:00:00.000Z",
    "end": "2025-09-18T09:05:27.000Z",
    "expiration": "2025-09-18T09:05:27.000Z",
    "stepStatuses": [
        {
            "commands": [
                {
                    "name": "fill",
                    "value": "Lorem ipsum",
                    "htmlElement": "The search field",
                    "screenshot": ["4b111ba4-c236-4770-67bf-0f17d0230e47"],
                }
            ],
            "status": "success",
            "start": "2025-09-18T09:01:02.000Z",
            "end": "2025-09-18T09:01:05.500Z",
            "assertionsReport": {
                "assertions": [{"assertion": 'The page title contains "Dashboard"', "checked": True}],
                "screenshot": "4b111ba4-c236-4770-67bf-0f17d0230e47",
            },
            "testVerdictCause": "Expected URL to contain /dashboard",
            "error": "internal",
        }
    ],
    "type": "manual",
    "steps": [
        {
            "action": 'Click on the "Login" button',
            "expectedResult": "Verify that the user is logged-in",
            "guidance": [{"text": "The user is between 18 and 49"}],
            "attachments": [{"name": "invoice_260313.pdf", "id": "string"}],
        }
    ],
}

TEST_RUNS = {
    "testRuns": [
        {
            "accountId": 256,
            "id": "5622",
            "status": "failed",
            "start": "2026-06-02T15:05:30.744Z",
            "end": "2026-06-02T15:07:26.720Z",
            "durationInSeconds": 116,
            "apiKeyId": None,
            "url": "https://www.google.com/",
            "source": "lynqa-platform",
            "name": "Failed BBC Article",
            "expiration": "2026-07-02T15:07:26.720Z",
            "isExpired": False,
        },
        {
            "accountId": 256,
            "id": "5615",
            "status": "failed",
            "start": "2026-06-02T13:36:22.717Z",
            "end": "2026-06-02T13:39:20.930Z",
            "durationInSeconds": 179,
            "apiKeyId": None,
            "url": "https://www.google.com/",
            "source": "lynqa-platform",
            "name": "Test BBC Article",
            "expiration": "2026-07-02T13:39:20.930Z",
            "isExpired": False,
        },
    ],
    "nextCursor": 2,
}

STEP_REPORT = {
    "commands": [
        {
            "name": "fill",
            "value": "Lorem ipsum",
            "htmlElement": "The search field",
            "screenshot": ["4b111ba4-c236-4770-67bf-0f17d0230e47"],
        }
    ],
    "status": "failed",
    "start": "2025-09-18T09:01:02.000Z",
    "end": "2025-09-18T09:01:05.500Z",
    "assertionsReport": {
        "assertions": [
            {"assertion": 'The page title contains "Dashboard"', "checked": True},
            {"assertion": 'The page title doesn\'t contain "Profil"', "checked": False},
        ],
        "screenshot": "4b111ba4-c236-4770-67bf-0f17d0230e47",
    },
    "testVerdictCause": "Expected URL to contain /dashboard",
    "error": "internal",
}

CREDIT_LEDGER_ENTRIES = [
    {
        "id": "cmpwd475u000o01p92xnxcbv7",
        "accountId": 256,
        "type": "CONSUMPTION",
        "amount": -1,
        "balanceAfter": 9,
        "testRunId": 5588,
        "metadata": {"source": "free-credits"},
        "createdAt": "2026-06-02T08:15:17.058Z",
    },
    {
        "id": "cmpp7a7vh000h26o7leija9to",
        "accountId": 256,
        "type": "ADJUSTMENT",
        "amount": 10,
        "balanceAfter": 10,
        "testRunId": None,
        "metadata": {"source": "admin-adjustment"},
        "createdAt": "2026-05-28T07:57:36.989Z",
    },
]
