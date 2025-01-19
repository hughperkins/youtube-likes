from typing import cast


JSON = dict[str, 'JSON'] | list['JSON'] | str | int | None | float


class Json:
    def __init__(self, data: JSON):
        self.data = data

    def __getattr__(self, k: str) -> 'Json':
        return Json(cast(dict[str, JSON], self.data)[k])

    def __getitem__(self, i: int | str) -> 'Json':
        if isinstance(i, int):
            res = cast(list[JSON], self.data)[i]
            # if isinstance(res, list) or isinstance(res, dict):
            return Json(res)
            # return res
        else:
            return Json(cast(dict[str, JSON], self.data)[i])

    def unwrap_int(self) -> int:
        return cast(int, self.data)

    def unwrap_str(self) -> str:
        return cast(str, self.data)

    def __iter__(self):
        # print('__iter__')
        for child in cast(list[JSON], self.data):
            yield Json(child)

    def keys(self) -> list[str]:
        return list(cast(dict[str, JSON], self.data).keys())

    def __contains__(self, k) -> bool:
        # print('__contains__', k)
        return k in cast(dict[str, JSON], self.data)
