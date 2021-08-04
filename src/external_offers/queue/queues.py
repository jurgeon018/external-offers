from cian_core.rabbitmq.consumer import Queue

from external_offers.helpers.queue import get_modified_queue_name, get_bindings
from external_offers.queue.routing_keys import AnnouncementReportingV1RoutingKey


process_announcements_queue = Queue(
    name=get_modified_queue_name('process_announcement_v2'),
    bindings=get_bindings('announcements', 'announcement_reporting', AnnouncementReportingV1RoutingKey),
)
