"""M13 agentops. Skeleton with probes only; behaviour arrives with P05.05."""

from scd_agentops.base import Service

service = Service("agentops", "M13")

if __name__ == "__main__":
    service.run()
