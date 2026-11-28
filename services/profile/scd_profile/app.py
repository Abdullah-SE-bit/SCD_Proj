"""M2 profile. Skeleton with probes only; behaviour arrives with P02.01."""

from scd_profile.base import Service

service = Service("profile", "M2")

if __name__ == "__main__":
    service.run()
