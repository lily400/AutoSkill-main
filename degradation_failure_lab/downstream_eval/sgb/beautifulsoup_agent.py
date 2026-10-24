"""Fail closed until Task-037 runtime, isolation and budget admission are reviewed."""
from downstream_eval.integration.terminus_compat import CompatibleTerminus2


class OfflineBeautifulSoupTerminus2(CompatibleTerminus2):
    def __init__(self, *args, **kwargs):
        # Do not inherit the P1 Git-pilot ledger or initialize a model client.
        raise RuntimeError('BeautifulSoup adapter is OFFLINE_ONLY; no Agent Trial is authorized or runtime-verified')
