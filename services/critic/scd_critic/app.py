"""M12 critic. Skeleton with probes only; behaviour arrives with P05.03."""

from scd_critic.base import Service

service = Service("critic", "M12")

if __name__ == "__main__":
    service.run()
