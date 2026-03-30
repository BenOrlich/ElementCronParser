import sys

if len(sys.argv) != 2:
    raise TypeError("Parser takes 1 argument: The current time in 24hr format, separated by a semicolon (e.g. 20 past 4 would be written as 16:20)")

# TODO: Handle incorrect time format

[current_hour, current_minute] = list(map(int, sys.argv[1].split(":")))

for job in sys.stdin.readlines():
    [minute_str, hour_str, command] = job.split(" ", 2)
    
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
        if today and job_hour == current_hour and job_minute < current_minute:
            if hour_wildcard:
                job_hour += 1
                if job_hour == 24:
                    today = False
                    job_hour = 0
            else:
                today = False
    print(f"{job_hour:02d}:{job_minute:02d} {"today" if today else "tomorrow"} - {command.rstrip()}")