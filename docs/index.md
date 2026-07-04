# Introduction

**robotframework-lynqa** is a [Robot Framework](https://robotframework.org) library for the
[Lynqa](https://lynqa.smartesting.com) test execution AI agent.

![Robot Framework/Lynqa connector](robotframework-lynqa.png#only-light)
![Robot Framework/Lynqa connector](robotframework-lynqa-dark.png#only-dark)

Write your scenarios in plain Gherkin and let Lynqa, [Smartesting](https://www.smartesting.com)'s AI
test-execution agent, execute them autonomously. No need to implement local keywords, simply provide your web
application's URL. Lynqa analyses your test steps and application UI, then runs your test cases as a user would,
producing comprehensive execution evidence. UI changes are handled automatically, eliminating the need for test
automation maintenance.

It builds on [pylynqa](https://github.com/petit-robot/pylynqa), the Python client for the Lynqa REST API.

## Disclaimers

!!! important "This is an unofficial project."

    robotframework-lynqa is **not affiliated with, endorsed by, or maintained by
    [Smartesting](https://www.smartesting.com)**, the company that develops Lynqa. "Lynqa" and "Smartesting" are
    the property of their respective owners.

!!! note "Lynqa is a commercial product."

    Using this library requires a Lynqa account and an API key, and running tests consumes paid credits. See
    <https://my.lynqa.smartesting.com/integration> to create an API key.

## Requirements

- Python 3.9+
- Robot Framework 7+
- A Lynqa account and API key (test executions consume credits)

## Where to next

- [Getting started](getting-started.md) — install the library and run your first scenario.
- [Keyword reference](keywords.md) — the Gherkin keywords and the `LYNQA_*` configuration variables.

## License

Licensed under the [Apache License 2.0](https://github.com/petit-robot/robotframework-lynqa/blob/main/LICENSE).
