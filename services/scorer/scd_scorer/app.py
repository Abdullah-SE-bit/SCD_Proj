"""M10 scorer. Skeleton with probes only; behaviour arrives with P06.03."""

from scd_scorer.base import Service

service = Service("scorer", "M10")

if __name__ == "__main__":
    service.run()
