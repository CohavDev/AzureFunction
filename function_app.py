import azure.functions as func
import re
import json
import logging
from bs4 import BeautifulSoup

# -*- coding: utf-8 -*-

# Configure logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    try:
        req_body = req.get_json()
    except ValueError as e:
        logging.info("Request body is not valid JSON")
        return func.HttpResponse(
            "Error: Request body is not valid JSON", status_code=400
        )
    else:
        events_str_lst = req_body.get("events").get("body").get("value")

    if events_str_lst:
        # events_json = json.loads(events_str_lst)
        try:
            logging.info("processing events...")
            response_object = process_events(events_str_lst)
        except Exception as e:
            logging.error("Events Processing Failed")
            logging.error(e)
            return func.HttpResponse("Events Processing Failed", status_code=500)

        logging.info("returning response = SUCCESS")
        return func.HttpResponse(
            response_object, mimetype="application/json", status_code=200
        )
    else:
        logging.info("returning response = FAILED")
        return func.HttpResponse(
            "This HTTP triggered function executed without list of events. Pass events in the request body.",
            status_code=400,
        )

# Loop through all events and building json object with relevant data
def process_events(events: list) -> str:
    events_info_lst = []
    events_wrong_format_lst = []
    for event in events:
        try:
            proccess_one_event(event, events_wrong_format_lst, events_info_lst)
        except Exception as e:
            logging.error("proccess_one_event() failed")
            logging.error(e)
            if event["subject"]:
                events_wrong_format_lst.append(event["subject"])
    response_object = {"ok_list": events_info_lst, "bad_list": events_wrong_format_lst}
    return json.dumps(response_object)

def proccess_one_event(event:str, events_wrong_format_lst:list,events_info_lst:list):
    event_body = event["body"]
    event_info_array = extract_info_from_body(event_body)
    if event_info_array is None:
        events_wrong_format_lst.append(event["subject"])
        return
    for event_info in event_info_array:
        if event_info == None:
            events_wrong_format_lst.append(event["subject"])
        else:
            events_info_lst.append(event_info)
    return

# Fetch event's data from it's body
def extract_info_from_body(input: str):
    soup = BeautifulSoup(input, "html.parser")
    soup.find('table')
    soupText = soup.get_text(separator="\n", strip=True)
    logging.info(soupText)
    match_words = {
        "tech_name": "שם טכנאי",
        "mantis_number": "מנטיס",
        "client_name": "שם לקוח",
        "service_type": "סוג השירות",
        "vhcls_count": "כמות רכבים",
        "car_item": "מספר רכב",
    }
    # tech_name = find_word_after(soupText, match_words["tech_name"])
    tech_name = "הכנס שם טכנאי"
    mantis = find_word_after(soupText, match_words["mantis_number"])
    client = find_word_after(soupText, match_words["client_name"])
    service = find_word_after(soupText, match_words["service_type"])
    cars_count = find_word_after(soupText, match_words["vhcls_count"])
    logging.info("----------------match:")
    result = (tech_name, mantis, client, service, cars_count)
    logging.info(result)
    logging.info("end tech name")
    if any(x is None for x in [tech_name, mantis, client, service, cars_count]):
        # wrong format
        return None
    else:
        data_array = []
        data = {
            "tech_name": tech_name,
            "mantis": mantis,
            "client": client,
            "service": service,
        }
        for i in range(int(cars_count)):
            car_id_name = match_words["car_item"] + " " + str(i + 1)
            logging.info("---------" + car_id_name)
            car_license = find_word_after(soupText, car_id_name)
            logging.info(car_license)
            if car_license == None:
                return None
            else:
                data_copy = data.copy()
                data_copy["car_license"] = car_license
                data_array.append(data_copy)
        return data_array

# Helper function for finding the next line string after a match (regex)
def find_word_after(input: str, match_word: str):
    pattern = rf"{re.escape(match_word)}\n(.*)"
    match = re.search(pattern, input)
    return str(match.group(1)) if match else None
