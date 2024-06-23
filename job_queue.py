from typing import Optional

from litequeue import LiteQueue

from messages.duel_request_message import DuelRequestMessage


class DuelsQueue:

    def __init__(self, db_path):
        self.db_path = db_path
        self.queue = LiteQueue(filename_or_conn=db_path, memory=False)

    def __del__(self):
        self.prune(include_failed=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.prune(include_failed=False)

    def prune(self, include_failed):
        self.queue.prune(include_failed)

    def add(self, queue_item: DuelRequestMessage):
        self.queue.put(queue_item.json())

    def get(self) -> Optional[DuelRequestMessage]:
        task = self.queue.pop()
        if not task:
            return None
        duel_request = DuelRequestMessage.parse_raw(task.data)
        duel_request.message_id = task.message_id
        return duel_request

    def mark_failed(self, duel_request):
        message_id = duel_request.message_id
        self.queue.mark_failed(message_id)

    def mark_done(self, duel_request):
        message_id = duel_request.message_id
        self.queue.done(message_id)
