"""FlexILS Gateway Network Element (GNE) lookup; database-only, it does not need the vendor SDK."""

from math import cos, radians, sin
from typing import ClassVar

from structlog import get_logger

from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.optical.db import subscription_instances_by_block_type
from orchestrator.optical.products.product_blocks.optical_node.nokia_flexils import NokiaFlexIlsBlock

logger = get_logger(__name__)

Vector = tuple[float, float, float]

_MAX_GNE_CANDIDATES = 7


class FlexilsGneProvider:
    """Provide the Gateway Network Element (GNE) nodes to reach subtended FlexILS nodes.

    The GNE candidates are the already-created NokiaFlexIlsBlock subscriptions that
    carry at least one management IP and a known location. Distances are computed on
    the great-circle approximation of the unit sphere, so the closest GNEs can be
    tried first when a node cannot be reached directly.
    """

    _tid_ips_xyz_of_gnes: ClassVar[list[tuple[str, list[str], Vector]]] = []

    @classmethod
    def _initialize_cache(cls) -> None:
        """Populate the GNE cache from the NokiaFlexIlsBlock subscriptions in the database."""
        instances = subscription_instances_by_block_type("NokiaFlexIlsBlock", [SubscriptionLifecycle.ACTIVE])

        gnes: list[tuple[str, list[str], Vector]] = []
        for instance in instances:
            try:
                block = NokiaFlexIlsBlock.from_db(instance.subscription_instance_id)
            except Exception:  # noqa: BLE001
                logger.warning(
                    "Skipping unreadable NokiaFlexIlsBlock while building GNE cache",
                    subscription_instance_id=str(instance.subscription_instance_id),
                )
                continue

            management_ips = [
                ip
                for ip in (
                    block.management.optical_module_node_dcn_interface_ip,
                    block.management.optical_module_node_dcn_loopback_ip,
                )
                if ip is not None
            ]
            if not management_ips:
                continue

            location = block.location
            if location is None or location.latitude is None or location.longitude is None:
                continue

            try:
                lat = radians(float(location.latitude))
                lon = radians(float(location.longitude))
            except (TypeError, ValueError):
                logger.warning(
                    "Skipping NokiaFlexIlsBlock with invalid location coordinates",
                    subscription_instance_id=str(instance.subscription_instance_id),
                    latitude=location.latitude,
                    longitude=location.longitude,
                )
                continue

            cos_lat = cos(lat)
            vector = (cos_lat * cos(lon), cos_lat * sin(lon), sin(lat))
            gnes.append((block.optical_flexils_target_id, management_ips, vector))

        cls._tid_ips_xyz_of_gnes = gnes
        logger.debug("Initialized FlexilsGneProvider cache", gnes=[tid for tid, _, _ in gnes])

    @classmethod
    def find_closest_gnes(cls, latitude: float, longitude: float) -> list[tuple[str, list[str]]]:
        """Return the (tid, management ips) pairs of the closest GNE nodes to the given coordinates.

        Args:
            latitude: Latitude of the target location in degrees.
            longitude: Longitude of the target location in degrees.

        Returns:
            List of (tid, management ips) tuples ordered from closest to farthest.
            Empty list if no GNE nodes are known.
        """
        if not cls._tid_ips_xyz_of_gnes:
            cls._initialize_cache()

        if not cls._tid_ips_xyz_of_gnes:
            return []

        lat = radians(latitude)
        lon = radians(longitude)
        cos_lat = cos(lat)
        target_vector = (cos_lat * cos(lon), cos_lat * sin(lon), sin(lat))

        def dot_product(candidate: Vector) -> float:
            return target_vector[0] * candidate[0] + target_vector[1] * candidate[1] + target_vector[2] * candidate[2]

        ordered = sorted(cls._tid_ips_xyz_of_gnes, key=lambda item: dot_product(item[2]), reverse=True)
        return [(tid, ip) for tid, ip, _ in ordered[:_MAX_GNE_CANDIDATES]]
