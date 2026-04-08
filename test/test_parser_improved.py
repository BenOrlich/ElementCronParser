from typing import Callable

import pytest
from src.parser import parse_line as basic
from src.parser_improved import parse_line as improved


@pytest.mark.parametrize("parse_line", [basic, improved], ids=["basic","improved"])
@pytest.mark.parametrize(
    ["time", "line", "expected"],
    [
        pytest.param((16, 10), "30 1 /bin/run_me_daily", "1:30 tomorrow - /bin/run_me_daily", id="example_daily (hour: past, minute: fixed)"),
        pytest.param((16, 10), "45 * /bin/run_me_hourly", "16:45 today - /bin/run_me_hourly", id="example_hourly (hour: wildcard, minute: future)"),
        pytest.param((16, 10), "* * /bin/run_me_every_minute", "16:10 today - /bin/run_me_every_minute", id="example_every_minute (both wildcard)"),
        pytest.param((16, 10), "* 19 /bin/run_me_sixty_times", "19:00 today - /bin/run_me_sixty_times", id="example_sixty_times (hour: future, minute: wildcard)"),
        pytest.param((23, 30), "10 * /bin/day_end_wildcard", "0:10 tomorrow - /bin/day_end_wildcard", id="day_end_wildcard (hour: wildcard, minute: past, current: 11pm)"),
        pytest.param((23, 30), "10 23 /bin/day_end_fixed", "23:10 tomorrow - /bin/day_end_fixed", id="day_end (hour: current, minute: past)"),
        pytest.param((23, 30), "10 /bin/missing_part", "Incorrect format: 10 /bin/missing_part", id="missing_part (failure)"),
        pytest.param((23, 30), "10 a /bin/invalid_time_part", "Incorrect format: 10 a /bin/invalid_time_part", id="invalid_time_part (failure)")
    ]
)
def test_parse_line(parse_line: Callable[[int, int, str], tuple[str, bool]], time: tuple[int,int], line: str, expected: str) -> None:
    assert parse_line(time[0], time[1], line)[0] == expected