from datetime import datetime, time, timezone


class MakeNaive:
    @staticmethod
    async def make_naive_obj(obj: object) -> object:
        for k, v in obj.__dict__.items():
            if isinstance(v, datetime):
                if v.tzinfo is not None:
                    setattr(obj, k, v.astimezone(timezone.utc).replace(tzinfo=None))
            if isinstance(v, time):
                if v.tzinfo is not None:
                    setattr(obj, k, v.replace(tzinfo=None))
        return obj

    @staticmethod
    async def make_naive_dict(data: dict) -> dict:
        for k, v in data.items():
            if isinstance(v, datetime):
                if v.tzinfo is not None:
                    data[k] = v.astimezone(timezone.utc).replace(tzinfo=None)
            if isinstance(v, time):
                if v.tzinfo is not None:
                    data[k] = v.replace(tzinfo=None)
        return data
