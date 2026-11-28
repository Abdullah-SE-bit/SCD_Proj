"""M6i ingestion job. Skeleton only; behaviour arrives with P04.03."""

import json


def main() -> int:
    print(json.dumps({"job": "ingestion", "status": "skeleton", "message": "nothing to do yet"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
