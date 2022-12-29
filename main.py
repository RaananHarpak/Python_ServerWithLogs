from flask import Flask
from flask import request, make_response
import json
import logging
import time
import os

app = Flask(__name__)
stack = []
global_counter = 1


def add_global_counter():
    global global_counter
    global_counter = int(global_counter) + 1


#region create logs folder:
folder_name = "logs"
if not os.path.isdir(folder_name):
    os.mkdir(folder_name)
#endregion


#region Init loggers and handlers

# ---------- request-logger --------------------
# create 2 logger:(also for printing)
req_logger = logging.getLogger('request-logger')
req_logger.setLevel(logging.INFO)
# Create a handler to write the log messages to a file
req_handler = logging.FileHandler('logs/requests.log')
# create handler for console
consoleHandler = logging.StreamHandler()
req_handler.setLevel(logging.INFO)
consoleHandler.setLevel((logging.INFO))
# Create a formatter to specify the format of the log messages
formatter = logging.Formatter(f'%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', "%d-%m-%Y %H:%M:%S")
# Add the formatter to the file handler
req_handler.setFormatter(formatter)
consoleHandler.setFormatter(formatter)
# Add the file handler to the logger
req_logger.addHandler(req_handler)
req_logger.addHandler(consoleHandler)


# ---------- stack-logger -------------------
# create logger:
stack_logger = logging.getLogger('stack-logger')
stack_logger.setLevel(logging.INFO)
# Create a handler to write the log messages to a file
stack_handler = logging.FileHandler('logs/stack.log')
stack_handler.setLevel(logging.INFO)
# Create a formatter to specify the format of the log messages
formatter = logging.Formatter(f'%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', "%d-%m-%Y %H:%M:%S")
# Add the formatter to the file handler
stack_handler.setFormatter(formatter)
# Add the file handler to the logger
stack_logger.addHandler(stack_handler)


# ---------- independent-logger -------------------
# create logger:
independent_logger = logging.getLogger('independent-logger')
independent_logger.setLevel(logging.DEBUG)
# Create a handler to write the log messages to a file
independent_handler = logging.FileHandler('logs/independent.log')
independent_handler.setLevel(logging.DEBUG)
# Create a formatter to specify the format of the log messages
formatter = logging.Formatter(f'%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', "%d-%m-%Y %H:%M:%S")
# Add the formatter to the file handler
independent_handler.setFormatter(formatter)
# Add the file handler to the logger
independent_logger.addHandler(independent_handler)
#endregion


@app.route('/independent/calculate', methods=['POST'])  # send via json 2 args and operation
def a():
    start_time = time.time()
    data_from_json = request.get_json()
    input_argument = data_from_json['arguments']
    input_operator = data_from_json['operation']
    arg_length = len(input_argument)
    message = ""
    code = 200
    result = ''

    if arg_length > 2:
        code = 409
        message = f'Error: Too many arguments to perform the operation {input_operator} | request #{global_counter}'

    elif input_operator.lower() == 'plus':
        if arg_length < 2:
            message = f'Error: Not enough arguments to perform the operation {input_operator} | request #{global_counter}'
            code = 409
        else:
            result = input_argument[0]+input_argument[1]

    elif input_operator.lower() == "minus":
        if arg_length < 2:
            code = 409
            message = f'Error: Not enough arguments to perform the operation {input_operator} | request #{global_counter}'
        else:
            result = input_argument[0]-input_argument[1]

    elif input_operator.lower() == "times":
        if arg_length < 2:
            code = 409
            message = f'Error: Not enough arguments to perform the operation {input_operator} | request #{global_counter}'
        else:
            result = input_argument[0]*input_argument[1]

    elif input_operator.lower() == "divide":
        if arg_length != 2:
            code = 409
            message = f'Error: Not enough arguments to perform the operation {input_operator}'
        elif input_argument[1] == 0:
            code = 409
            message = f'Error while performing operation Divide: division by 0'
        else:
            result = input_argument[0]/input_argument[1]

    elif input_operator.lower() == "pow":
        if arg_length < 2:
            code = 409
            message = f'Error: Not enough arguments to perform the operation {input_operator}'
        else:
            result = pow(input_argument[0], input_argument[1])

    elif input_operator.lower() == "abs":
        if arg_length != 1:
            code = 409
            message = f'Error: Too many arguments to perform the operation {input_operator} | request #{global_counter}'
        else:
            result = abs(input_argument[0])

    elif input_operator.lower() == "fact":
        fact = 1
        if arg_length != 1:
            code = 409
            message = f'Error: Too many arguments to perform the operation {input_operator} | request #{global_counter}'
        if input_argument[0] < 0:
            code = 409
            message = f'Error while performing operation Factorial: not supported for the negative number'
        else:
            for i in range(1, input_argument[0]+1):
                fact = fact * i
            result = fact

    else:
        code = 409
        message = f'Error: unknown operation: {input_operator}'

    if code == 409:
        body = {'error-message': message}
        stack_logger.error(f'Server encountered an error ! message: {message} | request #{global_counter}')
    elif code == 200:
        body = {'result': int(result)}
        independent_logger.info(f'Performing operation {str(input_operator)}. Result is {int(result)} | request #{global_counter}')
        independent_logger.debug(f'Performing operation: {str(input_operator)}({input_argument[0]},{input_argument[1]}) = {int(result)} | request #{global_counter}')
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000   # Calculate the elapsed time in milliseconds
    req_logger.info(f'Incoming request | #{global_counter} | resource: /independent/calculate | HTTP Verb POST  | request #{global_counter}')
    req_logger.debug(f'request #{global_counter} duration: {elapsed_time}ms  | request #{global_counter}')
    add_global_counter()
    return make_response(json.dumps(body), code)


@app.route('/stack/size', methods=['GET'])  # without some input, returns the size of stack
def b():
    start_time = time.time()
    code = 200
    body = {'result': len(stack)}
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Calculate the elapsed time in milliseconds
    stack_logger.info(f'Stack size is {len(stack)} | request #{global_counter}')
    stack_logger.debug(f"Stack content (first == top): {list(reversed(stack))} | request #{global_counter}")
    # cannot be error?
    req_logger.info(f'Incoming request | #{global_counter} | resource: /stack/size | HTTP Verb GET | request #{global_counter}')
    req_logger.debug(f'request #{global_counter} duration: {int(elapsed_time)}ms | request #{global_counter}')
    add_global_counter()
    return make_response(json.dumps(body), code)


@app.route('/stack/arguments', methods=['PUT'])  # send via json only 2 args and add them to stack
def c():
    start_time = time.time()
    data_from_json = request.get_json()
    input_argument = data_from_json['arguments']
    code = 200
    for i in range(len(input_argument)):
        stack.append(int(input_argument[i]))
    body = {'result': len(stack)}
    stack_logger.info(f'Adding total of {len(input_argument)} argument(s) to the stack | Stack size: {len(stack)} | request #{global_counter}')
    x = stack.pop()
    y = stack.pop()
    stack.append(y)
    stack.append(x)
    stack_logger.debug(f"Adding arguments: {y},{x} | Stack size before {len(stack) - len(input_argument)} | stack size after {len(stack)} | request #{global_counter}")
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Calculate the elapsed time in milliseconds
    req_logger.info(f'Incoming request | #{global_counter} | resource: /stack/arguments | HTTP Verb PUT | request #{global_counter}')
    req_logger.debug(f'request #{global_counter} duration: {int(elapsed_time)}ms | request #{global_counter}')
    add_global_counter()
    return make_response(json.dumps(body), code)


@app.route('/stack/operate', methods=['GET'])  # send via query params the operation and calc from stack.
def d():
    start_time = time.time()
    operation = request.args['operation']
    message = ""
    code = 200
    y_defined = True
    if str(operation).lower() == "plus":
        if len(stack) < 2:
            code = 409
            message = f'Error: cannot implement operation {operation}.It requires 2 arguments and the stack has only {len(stack)} arguments'
        else:
            x = stack.pop()
            y = stack.pop()
            result = x+y
    elif str(operation).lower() == "minus":
        if len(stack) < 2:
            code = 409
            message = f'Error: cannot implement operation {operation}. It requires 2 arguments and the stack has only {len(stack)} arguments'
        else:
            x = stack.pop()
            y = stack.pop()
            result = x - y
    elif str(operation).lower() == "times":
        if len(stack) < 2:
            code = 409
            message = f'Error: cannot implement operation {operation}. It requires 2 arguments and the stack has only {len(stack)} arguments'
        else:
            x = stack.pop()
            y = stack.pop()
            result = x * y
    elif str(operation).lower() == "divide":
        if len(stack) < 2:
            code = 409
            message = f'Error: cannot implement operation {operation}. It requires 2 arguments and the stack has only {len(stack)} arguments'
        else:
            x = stack.pop()
            y = stack.pop()
            if y == 0:
                code = 409
                message = f'Error while performing operation Divide: division by 0'
            else:
                result = x / y
    elif str(operation).lower() == "pow":
        if len(stack) < 2:
            code = 409
            message = f'Error: cannot implement operation {operation}. It requires 2 arguments and the stack has only {len(stack)} arguments'
        else:
            x = stack.pop()
            y = stack.pop()
            result = pow(x, y)
    elif str(operation).lower() == "abs":
        if len(stack) < 1:
            code = 409
            message = f'Error: cannot implement operation {operation}. It requires 1 arguments and the stack has only {len(stack)} arguments'
        else:
            x = stack.pop()
            result = abs(x)
            y_defined = False
    elif str(operation).lower() == "fact":
        if len(stack) < 1:
            code = 409
            message = f'Error: cannot implement operation {operation}. It requires 1 arguments and the stack has only {len(stack)} arguments'
        else:
            x = stack.pop()
            fact=1
            for i in range(1, x+1):
                fact = fact * i
            result = fact
            y_defined = False
    else:
        code = 409
        message = f'Error: unknown operation: {operation}'

    if code == 409:
        body = {'error-message': message}
        stack_logger.error(f'Server encountered an error ! message: {message} | request #{global_counter}')
    elif code == 200:
        body = {'result': int(result)}
        stack_logger.info(f'Performing operation {str(operation)}. Result is {int(result)} | stack size: {len(stack)} | request #{global_counter}')
        if y_defined is True:
            stack_logger.debug(f'Performing operation: {str(operation)}({x},{y}) = {int(result)} | request #{global_counter}')
        elif y_defined is False:
            stack_logger.debug(f'Performing operation: {str(operation)}({x}) = {int(result)} | request #{global_counter}')
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Calculate the elapsed time in milliseconds
    req_logger.info(f'Incoming request | #{global_counter} | resource: /stack/operate | HTTP Verb GET | request #{global_counter}')
    req_logger.debug(f'request #{global_counter} duration: {int(elapsed_time)}ms | request #{global_counter}')
    add_global_counter()
    return make_response(json.dumps(body), code)


@app.route('/stack/arguments', methods=['DELETE'])  # send via query params count(how many numbers to delete from stack)
def e():
    start_time = time.time()
    count = request.args['count']
    error_message = ""
    code = 200
    if len(stack) < int(count):
        code = 409
        error_message = f'Error: cannot remove {int(count)} from the stack. It has only {len(stack)} arguments'
    else:
        for i in range(int(count)):
            stack.pop()
    if code == 409:
        body = {'error-message': error_message}
        stack_logger.error(f'Server encountered an error ! message: {error_message} | request #{global_counter}')
    elif code == 200:
        body = {'result': len(stack)}
        stack_logger.info(f'Removing total {str(count)} argument(s) from the stack | Stack size: {len(stack)} | request #{global_counter}')
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Calculate the elapsed time in milliseconds
    req_logger.info(f'Incoming request | #{global_counter} | resource: /stack/arguments | HTTP Verb DELETE | request #{global_counter}')
    req_logger.debug(f'request #{global_counter} duration: {int(elapsed_time)}ms | request #{global_counter}')
    add_global_counter()
    return make_response(json.dumps(body), code)


@app.route('/logs/level', methods=['GET'])  # get level of logger
def G():
    start_time = time.time()
    code = 200
    logger_name = request.args['logger-name']

    try:
        log = logging.getLogger(logger_name + '.log')
        str_level = logging.getLevelName(log.getEffectiveLevel())
        body = {'Success': str(str_level).upper()}

    except Exception:
        code = 409
        body = {'Failure: An exception occurred - cannot get the logger name'}
        req_logger.error(f'Server encountered an error ! message: cannot get the level | request #{global_counter}')

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Calculate the elapsed time in milliseconds
    req_logger.info(f'Incoming request | #{global_counter} | resource: /logs/level | HTTP Verb GET | request #{global_counter}')
    req_logger.debug(f'request #{global_counter} duration: {int(elapsed_time)}ms | request #{global_counter}')
    add_global_counter()
    return make_response(json.dumps(body), code)


@app.route('/logs/level', methods=['PUT'])  # Sets the level of a logger
def H():
    start_time = time.time()
    logger_name = request.args['logger-name']
    logger_level = request.args['logger-level']
    upper_logger_level = str(logger_level).upper()
    code = 200

    if logger_level == 'INFO':
        set_level = logging.INFO
    elif logger_level == 'DEBUG':
        set_level = logging.DEBUG
    elif logger_level == 'ERROR':
        set_level = logging.ERROR
    else:
        code = 409
        body = {'Failure: An exception occurred - cannot set the logger name'}
        req_logger.error(f'Server encountered an error ! message: cannot set the level | request #{global_counter}')

    if logger_name == "request-logger":
        req_handler.setLevel(set_level)
        consoleHandler.setLevel(set_level)
        req_logger.setLevel(set_level)
        body = {'Success': upper_logger_level}

    elif logger_name == "stack-logger":
        stack_handler.setLevel(set_level)
        stack_logger.setLevel(set_level)
        body = {'Success': upper_logger_level}

    elif logger_name == "independent-logger":
        independent_handler.setLevel(set_level)
        independent_logger.setLevel(set_level)
        body = {'Success': upper_logger_level}
    else:
        code = 409
        body = {'Failure: An exception occurred - cannot set the logger name'}
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Calculate the elapsed time in milliseconds
    req_logger.info(f'Incoming request | #{global_counter} | resource: /logs/level | HTTP Verb PUT | request #{global_counter}')
    req_logger.debug(f'request #{global_counter} duration: {int(elapsed_time)}ms | request #{global_counter}')
    add_global_counter()
    return make_response(json.dumps(body), code)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=9583)

