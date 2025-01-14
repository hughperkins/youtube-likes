import abc
from youtube_likes_lib import string_lib
from youtube_likes_lib.yl_types import Output


class Analyzer(abc.ABC):
    def __init__(self, channel_abbrev: str, output: Output):
        self.channel_abbrev = channel_abbrev
        self.output = output

    @abc.abstractmethod
    def __call__(self, video_title: str, _letter: str, _old_value: int, _new_value: int) -> None:
        pass


class Mod100(Analyzer):
    def __call__(self, video_title: str, _letter: str, _old_value: int, _new_value: int):
        if (_new_value // 100 != _old_value // 100) and self.channel_abbrev not in ['RL']:
            self.output.priority_reasons_title += f" %100{_letter}"
            self.output.priority_reasons_desc += (
                f'- "{video_title}" %100{_letter}: {_new_value};\n'
            )
            self.output.is_priority = True


class Mod1000(Analyzer):
    def __call__(self, video_title: str, _letter: str, _old_value: int, _new_value: int):
        if (_new_value // 1000 != _old_value // 1000) and self.channel_abbrev not in ['RL']:
            self.output.priority_reasons_title += f" %1000{_letter}"
            self.output.priority_reasons_desc += (
                f'- "{video_title}" %1000{_letter}: {_new_value};\n'
            )
            self.output.is_priority = True


class Delta20(Analyzer):
    def __call__(self, video_title: str, _letter: str, _old_value: int, _new_value: int):
        _change = _new_value - _old_value
        _chg_str = string_lib.int_to_signed_str(_change)
        if _change >= 20 and self.channel_abbrev not in ['RL']:
            self.output.is_priority = True
            self.output.priority_reasons_title += f" 20{_letter}"
            self.output.priority_reasons_desc += f'- "{video_title}" 20{_letter} {_chg_str} => {_new_value};\n'


class Pct10(Analyzer):
    def __call__(self, video_title: str, _letter: str, _old_value: int, _new_value: int):
        _change = _new_value - _old_value
        _chg_str = string_lib.int_to_signed_str(_change)
        if _change > _old_value // 10:
            self.output.is_priority = True
            self.output.priority_reasons_title += f" 10p{_letter}"
            self.output.priority_reasons_desc += f'- "{video_title}" 10p{_letter} {_chg_str} => {_new_value};\n'
