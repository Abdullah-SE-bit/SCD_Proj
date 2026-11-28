"""M4 scouts. Skeleton with probes only; behaviour arrives with P04.02."""

from scd_scouts.base import Service

service = Service("scouts", "M4")

if __name__ == "__main__":
    service.run()
