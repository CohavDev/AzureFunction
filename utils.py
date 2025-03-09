from dateutil import parser
import re
from config import TECH_NAMES


class AppointmentsProcessor:
    def fetch_date(startDate: str):
        parsed_date = parser.parse(startDate)
        formatted_date = parsed_date.strftime("%d/%m/%Y")
        return formatted_date

    def fetch_tech_name(subject: str):
        tech_names = TECH_NAMES
        substring = [item for item in tech_names if item in subject]
        if len(substring) == 0:
            return None
        return substring[0]  # returns first match

    def find_word_after(input: str, match_word: str):
        pattern = rf"{re.escape(match_word)}\n(.*)"
        match = re.search(pattern, input)
        return str(match.group(1)) if match else None
