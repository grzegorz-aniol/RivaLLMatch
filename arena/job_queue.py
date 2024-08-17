from typing import Optional

from litequeue import LiteQueue

from messages.duel_request_message import DuelRequestMessage
from utils.logger import Logger


class DuelsQueue:
    logger = Logger()

    def __init__(self, db_path):
        self.db_path = db_path
        self.queue = LiteQueue(filename_or_conn=db_path, memory=False, queue_name="duels_queue")
        self.cnt_retried = 0

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
            if self.cnt_retried > 1:
                return None
            self.cnt_retried += 1
            self.retry_failed()
            task = self.queue.pop()
            if not task:
                return None
        duel_request = DuelRequestMessage.model_validate_json(task.data)
        duel_request.message_id = task.message_id
        return duel_request

    def mark_failed(self, duel_request):
        message_id = duel_request.message_id
        self.queue.mark_failed(message_id)

    def mark_done(self, duel_request):
        message_id = duel_request.message_id
        self.queue.done(message_id)

    def retry_failed(self):
        failed_messages = list(self.queue.list_failed())
        n_failed = len(failed_messages)
        if n_failed > 0:
            self.logger.info(f'Found {n_failed} failed messages. Retrying all of them...')
            for message in failed_messages:
                self.queue.retry(message.message_id)
            return True
        return False

    def retry_locked(self):
        locked_messages = list(self.queue.list_locked(0))
        n_locked = len(locked_messages)
        if n_locked > 0:
            self.logger.info(f'Found {n_locked} locked messages. Retrying all of them...')
            for message in locked_messages:
                self.queue.retry(message.message_id)
            return True
        return False
