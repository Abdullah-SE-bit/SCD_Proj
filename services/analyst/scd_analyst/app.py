"""M7 analyst. Skeleton with probes only; behaviour arrives with P07.01."""

from scd_analyst.base import Service

service = Service("analyst", "M7")

if __name__ == "__main__":
    service.run()
