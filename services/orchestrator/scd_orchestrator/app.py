"""M3 orchestrator. Skeleton with probes only; behaviour arrives with P05.02."""

from scd_orchestrator.base import Service

service = Service("orchestrator", "M3")

if __name__ == "__main__":
    service.run()
