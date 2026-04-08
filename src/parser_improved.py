from __future__ import annotations
from enum import Enum
import sys
from typing import Callable



class TimeUnitData:
    def __init__(self, max: int|Callable[[int|None], int]) -> None:
        self.max = max
    
    def getMax(self, parent_current: int|None) -> int:
        if isinstance(self.max, int):
            return self.max
        else:
            return self.max(parent_current)

class TimeUnit(Enum):
    MINUTE = TimeUnitData(59)
    HOUR = TimeUnitData(23)
    BASE = TimeUnitData(1)


class TimePart:
    class __PartType(Enum):
        FIXED = 0
        WILDCARD = 1
        FUTURE = 2
    
    class NotATimePartError(ValueError):
        pass
    
    def __init__(self, value: int, parent: TimePart|None, part_type: __PartType, unit: TimeUnit) -> None:
        if value > unit.value.getMax(parent.get_value() if parent is not None else None): raise self.NotATimePartError
        self.__value = value
        self.__unit = unit.value
        self.__parent = parent
        self.__part_type = part_type
        
    def __wildcard(self):
        if self.__parent is not None and self.__value >= self.__unit.getMax(self.__parent.get_value()):
            self.__value -= self.__unit.getMax(self.__parent.get_value())
            self.__parent.__increment()
        else:
            self.__value += 1
            
    def __fixed(self):
        if self.__parent is not None:
            self.__parent.__increment()
    
    def __increment(self):
        match self.__part_type:
            case self.__PartType.FIXED:
                self.__fixed()
            case self.__PartType.WILDCARD:
                self.__wildcard()
                
        self.__part_type = self.__PartType.FUTURE
    
    def parse_next(self, time_part_str: str, unit: TimeUnit, current_value: int) -> TimePart:
        if not self.is_time_part(time_part_str, unit, True, self): raise self.NotATimePartError
        
        match time_part_str, self.__part_type != self.__PartType.FUTURE:
            case "*", True:
                return TimePart(current_value, self, self.__PartType.WILDCARD, unit)
            
            case "*", False:
                return TimePart(0, self, self.__PartType.FUTURE, unit)
            
            case _, True:
                time_part = int(time_part_str)
                if time_part < current_value:
                    self.__increment()
                    return TimePart(time_part, self, self.__PartType.FUTURE, unit)
                else:
                    return TimePart(time_part, self, self.__PartType.FIXED if time_part == current_value else self.__PartType.FUTURE, unit)
            
            case _, False:
                time_part = int(time_part_str)
                return TimePart(time_part, self, self.__PartType.FUTURE, unit)
            
    @staticmethod
    def init_base() -> TimePart:
        return TimePart(0, None, TimePart.__PartType.WILDCARD, TimeUnit.BASE)
    
    @staticmethod
    def is_time_part(time: str, unit: TimeUnit, allow_wildcard:bool, previous: TimePart|None=None) -> bool:
        if allow_wildcard and time == "*": return True
        try:
            t = int(time)
        except ValueError:
            return False
        return 0 <= t <= unit.value.getMax(previous.get_value() if previous is not None else None)
    
    def get_value(self) -> int:
        return self.__value






def is_time(hour: str, minute: str, allow_wildcard:bool=False) -> bool:
    return TimePart.is_time_part(hour, TimeUnit.HOUR, allow_wildcard) and TimePart.is_time_part(minute, TimeUnit.MINUTE, allow_wildcard)


def parse_line(current_hour: int, current_minute: int, line: str) -> tuple[str, bool]:
    job = line.rstrip().split(" ", 2)
    failure_text = f"Incorrect format: {line.rstrip()}"
    if len(job) != 3:
        return failure_text, False
    else:
        minute_str, hour_str, command = job
        
        try:
            day = TimePart.init_base()
            hour = day.parse_next(hour_str, TimeUnit.HOUR, current_hour)
            minute = hour.parse_next(minute_str, TimeUnit.MINUTE, current_minute)
        except TimePart.NotATimePartError:
            return failure_text, False
        else:
            return f"{hour.get_value()}:{minute.get_value():02d} {"today" if day.get_value() == 0 else "tomorrow"} - {command}", True




if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise TypeError("Parser takes 1 argument: The current time in 24hr HH:MM format")

    current_time  = sys.argv[1].split(":")
    if len(current_time) != 2 or not is_time(current_time[0], current_time[1]):
        raise ValueError(f"{sys.argv[1]} is not a valid time, the time must be in 24hr HH:MM format")

    for job in sys.stdin.readlines():
        print(parse_line(int(current_time[0]), int(current_time[1]), job)[0])