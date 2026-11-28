"""M9 validators. Skeleton with probes only; behaviour arrives with P05.01."""

from scd_validators.base import Service

service = Service("validators", "M9")

if __name__ == "__main__":
    service.run()
