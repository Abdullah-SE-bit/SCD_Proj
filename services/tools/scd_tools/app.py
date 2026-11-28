"""M5 tools. Skeleton with probes only; behaviour arrives with P04.01."""

from scd_tools.base import Service

service = Service("tools", "M5")

if __name__ == "__main__":
    service.run()
