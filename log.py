filename = "api-logs.txt"

def log_raw_request(request, tag):
    with open(filename, "a") as file:
        file.write('Request_{}: {}\n'.format(tag, request.method + ' ' + request.url))


def log_raw_response(response, tag):
    with open(filename, "a") as file:
        file.write('Response_{}: {}\n'.format(tag, "URL " + response.url + '; STATUS CODE: ' + str(response.status_code)))

def reset_file():
    file = open(filename, "w+")
    file.truncate(0)
    file.close()

