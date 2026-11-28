"""M11 verdict. Skeleton with probes only; behaviour arrives with P03.01."""

from scd_verdict.base import Service

service = Service("verdict", "M11")

if __name__ == "__main__":
    service.run()
