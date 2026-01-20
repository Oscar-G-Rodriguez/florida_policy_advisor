from __future__ import annotations

from typing import List

from app.data.loaders import LOADERS


def refresh_all(allow_network: bool = True) -> List[dict]:
    results = []
    for loader in LOADERS:
        results.append(loader(allow_network=allow_network))
    return results


if __name__ == "__main__":
    for result in refresh_all(allow_network=True):
        print(result)
