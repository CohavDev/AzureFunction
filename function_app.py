import azure.functions as func
import re
import json
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Error: Request body is not valid JSON", status_code=400
        )
    else:
        events_str_lst = req_body.get("events")

    if events_str_lst:
        # events_json = json.loads(events_str_lst)
        try:
            response_object = process_events(events_str_lst)
        except Exception as e:
            return func.HttpResponse("Events Processing Failed", status_code=500)

        return func.HttpResponse(
            response_object, mimetype="application/json", status_code=200
        )
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed without list of events. Pass events in the request body.",
            status_code=400,
        )


def process_events(events: list) -> str:
    events_info_lst = []
    events_wrong_format_lst = []
    for event in events:
        print("event")
        print(event)
        event_body = event["body"]
        event_info = extract_info_from_body(event_body)
        if event_info == None:
            events_wrong_format_lst.append(event["subject"])
        else:
            events_info_lst.append(event_info)
    response_object = {"ok_list": events_info_lst, "bad_list": events_wrong_format_lst}
    return json.dumps(response_object)


def extract_info_from_body(input: str):
    match_words = {
        "tech_name": "שם טכנאי",
        "mantis_number": "מנטיס",
        "client_name": "שם לקוח",
        "service_type": "סוג השירות",
        "vhcls_count": "כמות רכבים",
        "car_item": "רכב מספר",
    }
    tech_name = find_word_after(input, match_words["tech_name"])
    mantis = find_word_after(input, match_words["mantis_number"])
    client = find_word_after(input, match_words["client_name"])
    service = find_word_after(input, match_words["service_type"])
    cars_count = find_word_after(input, match_words["vhcls_count"])
    if any(x is None for x in (tech_name, mantis, client, service, cars_count)):
        # wrong format
        return None
    else:
        data = {
            "tech_name": tech_name,
            "mantis": mantis,
            "client": client,
            "service": service,
        }
        for i in range(int(cars_count)):
            car_id_name = match_words["car_item"] + " " + i + 1
            car_license = find_word_after(input, car_id_name)
            if car_license == None:
                return None
            else:
                data[car_id_name] = car_license
        return json.dumps(data)


def find_word_after(input: str, match_word: str):
    pattern = rf"\b{re.escape(match_word)}\s+(\w+)"
    match = re.search(pattern, input)
    return match.group(1) if match else None
