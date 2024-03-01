# Write your code here

import json
import re
from datetime import datetime


class BusIdRule:

    def __init__(self):
        self.name = "bus_id"
        self.required = True
        self.pattern = "[0-9]+"
        self.errors = 0

    def check(self, json_val):
        if json_val is None:
            return False
        elif not isinstance(json_val, int):
            return False
        else:
            return True


class StopIdRule:

    def __init__(self):
        self.name = "stop_id"
        self.required = True
        self.pattern = "[0-9]+"
        self.errors = 0

    def check(self, json_val):
        if json_val is None:
            return False
        elif not isinstance(json_val, int):
            return False
        else:
            return True


class StopNameRule:

    def __init__(self):
        self.name = "stop_name"
        self.required = True
        self.pattern = "[A-Z][a-z]*( [A-Z][a-z]*)* (Road|Avenue|Boulevard|Street)"
        self.errors = 0

    def check(self, json_val):
        if json_val is None:
            return False
        elif not isinstance(json_val, str):
            return False
        else:
            return re.fullmatch(self.pattern, json_val)


class NextStopRule:

    def __init__(self):
        self.name = "next_stop"
        self.required = True
        self.pattern = "[0-9]+"
        self.errors = 0

    def check(self, json_val):
        if json_val is None:
            return False
        elif not isinstance(json_val, int):
            return False
        else:
            return True


class StopTypeRule:

    def __init__(self):
        self.name = "stop_type"
        self.required = False
        self.pattern = "(S|F|O)?"
        self.errors = 0

    def check(self, json_val):
        if json_val is None:
            return True
        elif not isinstance(json_val, str):
            return False
        else:
            return re.fullmatch(self.pattern, json_val)


class ATimeRule:

    def __init__(self):
        self.name = "a_time"
        self.required = True
        self.pattern = "[0-2][0-9]:[0-5][0-9]"
        self.errors = 0

    def check(self, json_val):
        if json_val is None:
            return False
        elif not isinstance(json_val, str):
            return False
        else:
            return re.fullmatch(self.pattern, json_val)


class Timetable:

    def __init__(self, ):
        self.lines = {}
        self.stop_options = {}

    def add_stop(self, stop):
        bus_id = stop.bus_id
        stop_id = stop.stop_id
        if bus_id not in self.lines.keys():
            self.lines[bus_id] = Line(bus_id)
        if stop_id not in self.stop_options.keys():
            self.stop_options[stop_id] = StopOption(stop_id, stop.stop_name)
        self.lines[bus_id].stops[stop_id] = stop
        return self.lines[bus_id]

    def start_stops(self):
        return list(map(lambda start: self.stop_options[start.stop_id], map(lambda a_line: a_line.start(), self.lines.values())))

    def transfer_stops(self):
        transfer = []
        for option in self.stop_options.values():
            if len(list(filter(lambda li: li.has_stop(option) is True, self.lines.values()))) > 1:
                transfer.append(option)
        return transfer

    def final_stops(self):
        return list(map(lambda final: self.stop_options[final.stop_id], map(lambda line: line.final(), self.lines.values())))

    def is_valid(self):
        return all(line.is_valid() for line in self.lines.values()) and len(self.stops_with_wrong_stop_type()) == 0

    def lines_without_start_stop(self):
        return list(filter(lambda line: line.has_start_and_stop() is False, self.lines.values()))
    
    def lines_with_invalid_schedule(self):
        return list(filter(lambda line: line.is_schedule_valid() is False, self.lines.values()))

    def stops_with_wrong_stop_type(self):
        wrong_stops = {}
        starts = {stop.stop_id: stop for stop in self.start_stops()}
        transfers = {stop.stop_id: stop for stop in self.transfer_stops()}
        finals = {stop.stop_id: stop for stop in self.final_stops()}
        special_stops = {**starts, **transfers, **finals}
        for a_line in self.lines.values():
            for a_stop in a_line.stops.values():
                if a_stop.is_on_demand() and a_stop.stop_id in special_stops:
                    wrong_stops[a_stop.stop_id] = a_stop
        return wrong_stops.values()


class StopOption:

    def __init__(self, stop_id, stop_name):
        self.stop_id = stop_id
        self.stop_name = stop_name


class Line:

    def __init__(self, bus_id):
        self.bus_id = bus_id
        self.stops = {}

    def start(self):
        return self.filter_start_stops()[0] if self.has_start_and_stop() else None

    def final(self):
        return self.filter_final_stops()[0] if self.has_start_and_stop() else None

    def is_valid(self):
        return self.has_start_and_stop() and self.is_schedule_valid()

    def has_start_and_stop(self):
        return (len(self.filter_start_stops()) == 1
                and len(self.filter_final_stops()) == 1)

    def is_schedule_valid(self):
        return self.stop_with_invalid_schedule() is None

    def stop_with_invalid_schedule(self):
        invalid_stop = None
        stop = self.start()
        final = self.final()
        while invalid_stop is None and stop is not final:
            next_stop = self.stops[stop.next_stop]
            if next_stop.time() < stop.time():
                invalid_stop = next_stop
            stop = next_stop
        return invalid_stop

    def filter_start_stops(self):
        return list(filter(lambda stop: stop.is_start() is True, self.stops.values()))

    def filter_final_stops(self):
        return list(filter(lambda stop: stop.is_final() is True, self.stops.values()))

    def has_stop(self, option):
        return any(stp.stop_id == option.stop_id for stp in self.stops.values())


class Stop:

    def __init__(self, data):
        self.bus_id = data.get("bus_id", None)
        self.stop_id = data.get("stop_id", None)
        self.stop_name = data.get("stop_name", None)
        self.next_stop = data.get("next_stop", None)
        self.stop_type = data.get("stop_type", None)
        self.a_time = data.get("a_time", None)

    def is_start(self):
        return self.stop_type == "S"

    def is_final(self):
        return self.stop_type == "F"

    def is_on_demand(self):
        return self.stop_type == "O"

    def time(self):
        return datetime.strptime(self.a_time, "%H:%M")


rules = [BusIdRule(), StopIdRule(), StopNameRule(), NextStopRule(), StopTypeRule(), ATimeRule()]

usr_in = input()
timetable_data = json.loads(usr_in)
for stop_data in timetable_data:
    for rule in rules:
        value = stop_data.get(rule.name, None)
        if not rule.check(value):
            rule.errors += 1

total_errors = sum(map(lambda r: r.errors, rules))
if total_errors > 0:
    print(f"Type and required field validation: {total_errors} errors")
    for rule in rules:
        print(f"{rule.name}: {rule.errors}")
else:
    timetable = Timetable()
    for stop_data in timetable_data:
        added_line = timetable.add_stop(Stop(stop_data))
    print("On demand stops test:")
    if timetable.is_valid():
        print("OK")
    else:
        invalid_stops = timetable.stops_with_wrong_stop_type()
        print(f"Wrong stop type: {sorted(map(lambda s: s.stop_name, invalid_stops))}")
