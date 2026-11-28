"""M6 kb. Skeleton with probes only; behaviour arrives with P04.04."""

from scd_kb.base import Service

service = Service("kb", "M6")

if __name__ == "__main__":
    service.run()
