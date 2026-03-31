import sys




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
        [minute_str, hour_str, command] = job
            
        today = True
        if hour_str == "*":
            job_hour = current_hour
            hour_wildcard = True
        else:
            job_hour = int(hour_str)
            if job_hour < current_hour:
                today = False
            hour_wildcard = False
            
        if minute_str == "*":
            job_minute = current_minute if job_hour == current_hour else 0
        else:
            job_minute = int(minute_str)
            if today and job_hour == current_hour and job_minute < current_minute: # Check if job time is in the past
                if hour_wildcard:
                    job_hour += 1
                    if job_hour == 24:
                        today = False
                        job_hour = 0
                else:
                    today = False
                    
        print(f"{job_hour:02d}:{job_minute:02d} {"today" if today else "tomorrow"} - {command}")


def parse_line_2(current_hour: int, current_minute: int, line: str) -> None:
    job = line.rstrip().split(" ", 2)
    if len(job) != 3 or not is_time(job[1], job[0], True):
        print(f"Incorrect format: {line.rstrip()}")
    else:
        minute_str, hour_str, command = job
        
        if hour_str == "*":
            job_hour = current_hour
            current = True
            today = True
        else:
            job_hour = int(hour_str)
            today = job_hour >= current_hour
            current = job_hour == current_hour
        
        match minute_str, current, hour_str, job_hour:
            case "*", True, *_:
                job_minute = current_minute
            case "*", False, *_:
                job_minute = 0
            case _, True, "*", 23:
                pass
            case _, True:
                job_minute = int(minute_str)
                if job_minute < current_minute:
                    today = False
            case _, False, *_:
                job_minute = int(minute_str)
                
                    
        print(f"{job_hour:02d}:{job_minute:02d} {"today" if today else "tomorrow"} - {command}")




if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise TypeError("Parser takes 1 argument: The current time in 24hr HH:MM format")

    current_time  = sys.argv[1].split(":")
    if len(current_time) != 2 or not is_time(current_time[0], current_time[1]):
        raise ValueError(f"{sys.argv[1]} is not a valid time, the time must be in 24hr HH:MM format")

    for job in sys.stdin.readlines():
        parse_line(int(current_time[0]), int(current_time[1]), job)