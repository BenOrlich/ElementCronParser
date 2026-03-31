from __future__ import annotations
from enum import Enum
import sys




class TimePart:
    class __IncrementType(Enum):
        FIXED = 0
        WILDCARD = 1
        NONE = 2
    
    def __init__(self, value: int, parent: TimePart|None, increment_type: __IncrementType, max:int) -> None:
        self.value = value
        self.__max = max
        self.__parent = parent
        self.__increment_type = increment_type
        
    def __wildcard(self):
        if self.value == self.__max:
            self.value = 0
            if self.__parent is not None:
                self.__parent.__increment()
        else:
            self.value += 1
            
    def __fixed(self):
        if self.__parent is not None:
            self.__parent.__increment()
    
    def __increment(self):
        match self.__increment_type:
            case self.__IncrementType.FIXED:
                self.__fixed()
            case self.__IncrementType.WILDCARD:
                self.__wildcard()
    
    def parse_next_time_part(self, time_part_str: str, max: int, current_time_part: int, possibly_current: bool) -> tuple[TimePart, bool]:
        match time_part_str, possibly_current:
            case "*", True:
                return TimePart(current_time_part, self, self.__IncrementType.WILDCARD, max), True
            case "*", False:
                return TimePart(0, self, self.__IncrementType.NONE, max), False
            case _, True:
                time_part = int(time_part_str)
                if time_part < current_time_part:
                    self.__increment()
                    return TimePart(time_part, self, self.__IncrementType.NONE, max), False
                else:
                    return TimePart(time_part, self, self.__IncrementType.FIXED if time_part == current_time_part else self.__IncrementType.NONE, max), time_part == current_time_part
            case _, False:
                time_part = int(time_part_str)
                return TimePart(time_part, self, self.__IncrementType.NONE, max), False
    @staticmethod
    def init_base_time_part(initial_value: int) -> TimePart:
        return TimePart(initial_value, None, TimePart.__IncrementType.WILDCARD, initial_value+1)
    
    def get_value(self) -> int:
        return self.value




def is_time_part(time: str, max: int, allow_wildcard:bool) -> bool:
    if allow_wildcard and time == "*": return True
    
    try:
        t = int(time)
    except ValueError:
        return False
    
    return 0 <= t <= max


def is_time(hour: str, minute: str, allow_wildcard:bool=False) -> bool:
    return is_time_part(hour, 24, allow_wildcard) and is_time_part(minute, 60, allow_wildcard)


def parse_line(current_hour: int, current_minute: int, line: str) -> None:
    job = line.rstrip().split(" ", 2)
    if len(job) != 3 or not is_time(job[1], job[0], True):
        print(f"Incorrect format: {line.rstrip()}")
    else:
        minute_str, hour_str, command = job
            
        day = TimePart.init_base_time_part(0)
        hour, potentially_current = day.parse_next_time_part(hour_str, 23, current_hour, True)
        minute, _ = hour.parse_next_time_part(minute_str, 59, current_minute, potentially_current)
                    
        print(f"{hour.get_value():02d}:{minute.get_value():02d} {"today" if day.get_value() == 0 else "tomorrow"} - {command}")




if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise TypeError("Parser takes 1 argument: The current time in 24hr HH:MM format")

    current_time  = sys.argv[1].split(":")
    if len(current_time) != 2 or not is_time(current_time[0], current_time[1]):
        raise ValueError(f"{sys.argv[1]} is not a valid time, the time must be in 24hr HH:MM format")

    for job in sys.stdin.readlines():
        parse_line(int(current_time[0]), int(current_time[1]), job)