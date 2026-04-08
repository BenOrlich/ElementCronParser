import pytest
from src.parser_improved import parse_line

@pytest.mark.parametrize(
    ["time", "line", "expected"],
    [
        pytest.param((16, 10), "30 1 /bin/run_me_daily", "1:30 tomorrow - /bin/run_me_daily", id="example_daily"),
        pytest.param((16, 10), "45 * /bin/run_me_hourly", "16:45 today - /bin/run_me_hourly", id="example_hourly"),
        pytest.param((16, 10), "* * /bin/run_me_every_minute", "16:10 today - /bin/run_me_every_minute", id="example_every_minute"),
        pytest.param((16, 10), "* 19 /bin/run_me_sixty_times", "19:00 today - /bin/run_me_sixty_times", id="example_sixty_times")
    ]
)
def test_parse_line(time: tuple[int,int], line: str, expected: str) -> None:
    assert parse_line(time[0], time[1], line)[0] == expected