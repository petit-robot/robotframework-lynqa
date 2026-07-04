# robotframework-lynqa

[![CI](https://github.com/petit-robot/robotframework-lynqa/actions/workflows/ci.yml/badge.svg)](https://github.com/petit-robot/robotframework-lynqa/actions/workflows/ci.yml)
[![Acceptance test](https://github.com/petit-robot/robotframework-lynqa/actions/workflows/acceptance.yml/badge.svg)](https://github.com/petit-robot/robotframework-lynqa/actions/workflows/acceptance.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-Full%20documentation-blue.svg)](https://petit-robot.github.io/robotframework-lynqa/)

**robotframework-lynqa** is a [Robot Framework](https://robotframework.org) library for the
[Lynqa](https://lynqa.smartesting.com) test execution AI Agent.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/petit-robot/robotframework-lynqa/main/docs/robotframework-lynqa-dark.png">
  <img alt="Robot Framework/Lynqa connector" src="https://raw.githubusercontent.com/petit-robot/robotframework-lynqa/main/docs/robotframework-lynqa.png">
</picture>

Write your scenarios in plain Gherkin and let Lynqa, [Smartesting](https://www.smartesting.com)'s AI test-execution agent, execute them autonomously.
No need to implement local keywords, simply provide your web application's URL.
Lynqa analyses your test steps and application UI, then runs your test cases as a user would, producing comprehensive execution evidence.
UI changes are handled automatically, eliminating the need for test automation maintenance.

It builds on [pylynqa](https://github.com/petit-robot/pylynqa), the Python client for the Lynqa REST API.

## Disclaimers

> [!IMPORTANT]
> **This is an unofficial project.** robotframework-lynqa is **not affiliated with, endorsed by, or maintained by
> [Smartesting](https://www.smartesting.com)**, the company that develops Lynqa. "Lynqa" and "Smartesting" are the
> property of their respective owners.

> [!NOTE]
> **Lynqa is a commercial product.** Using this library requires a Lynqa account and an API key, and running tests
> consumes paid credits. See <https://my.lynqa.smartesting.com/integration> to create an API key.

## Requirements

- Python 3.9+
- Robot Framework 7+
- A Lynqa account and API key (test executions consume credits)

## Installation

```bash
pip install robotframework-lynqa
```

## Quick start

Import the library and write your test cases with the `Given`/`When`/`Then` keywords, each taking a single
natural-language step:

```robotframework
*** Settings ***
Library    robotframework_lynqa.LynqaLibrary    api_key=%{LYNQA_API_KEY}

*** Variables ***
${LYNQA_URL}    https://lemonde.fr

*** Test Cases ***
Search An Article
    Given    the website is open
    When     I search an article on "france ia"
    Then     there is an article on "IA agentique"
```

The scenario is captured and submitted to Lynqa, which runs it against the site at `${LYNQA_URL}` and reports each step's
result back to Robot Framework.

## Documentation

Full documentation: installation, configuration variables and the complete keyword reference — is available at
<https://petit-robot.github.io/robotframework-lynqa/>.

## Collaboration

This project is at an early stage, so **external contributions are limited for now**. This may be opened up more broadly
later as the project matures.

In the meantime, **you are very welcome to open an
[issue](https://github.com/petit-robot/robotframework-lynqa/issues)** to report a bug or ask any question.

## License

Licensed under the [Apache License 2.0](LICENSE).
