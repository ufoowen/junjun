*** Settings ***
Library           RequestsLibrary

*** Test Cases ***
Mytest
    ${dic}    Create dictionary    Content-type=application/json
    Create Session    baidu    http://www.baidu.com
    ${getsValue}    Get Request    baidu    /    headers=${dic}
    log    ${getsValue.status_code}
