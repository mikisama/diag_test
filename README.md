# Diagnostic test python

This provide a basic Automated Testing Method for [ISO-TP](https://en.wikipedia.org/wiki/ISO_15765-2) and [UDS](https://en.wikipedia.org/wiki/Unified_Diagnostic_Services) Protocol Stack

## Requirement

1. [python 3.7+](https://www.python.org/downloads/)
2. [poetry](https://github.com/python-poetry/poetry)
3. [CAN Interface](https://python-can.readthedocs.io/en/stable/interfaces.html) supported by python-can

## Quick Start

```bash
$ git clone
$ # use poetry to install python dependencies pack
$ poetry install
$ # run the isotp test
$ python isotp_test.py
$ # run the uds test
$ python diag_test.py
```

## UDS Service under test

| SID(hex) | Service                    | Sub-function(hex) | Security Access | Default Session | Program Session | Extended Session | Functional Addressing |
| -------- | -------------------------- | ----------------- | --------------- | --------------- | --------------- | ---------------- | --------------------- |
| 10       | DiagnositicSessionControl  | 01/02/03          | /               | √               | √               | √                | √                     |
| 11       | ECUReset                   | 01/03             | /               | √               | √               | √                | /                     |
| 14       | ClearDiagnosticInformation | /                 | /               | √               | √               | √                | √                     |
| 19       | ReadDTCInformation         | 02/0A             | /               | √               | √               | √                | /                     |
| 22       | ReadDataByIdentifier       | /                 | /               | √               | √               | √                | /                     |
| 2E       | WriteDataByIdentifier      | /                 | 03/04           | /               | /               | √                | /                     |
| 27       | SecurityAccess             | 03/04             | /               | /               | √               | √                | /                     |
| 28       | CommunicationControl       | 00/03             | /               | /               | √               | √                | √                     |
| 3E       | TesterPresent              | 00/80             | /               | √               | √               | √                | √                     |
| 85       | ControlDTCSetting          | 01/02             | /               | /               | /               | √                | √                     |
| 31       | RoutineControl             | 01/02/03          | 03/04           | /               | √               | √                | /                     |
