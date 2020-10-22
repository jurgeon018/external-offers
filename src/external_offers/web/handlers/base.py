from typing import Any, Dict, Optional

from cian_core.web.base_handlers import PublicHandler as BasePublicHandler
from cian_json import json


class PublicHandler(BasePublicHandler):
    # pylint: disable=abstract-method

    @property
    def realty_user_id(self) -> int:
        value = self.request.headers['X-Real-UserId']
        return int(value)

    async def prepare(self) -> None:
        super().prepare()

        error_data = await self._check_authorization()
        if error_data:
            self.set_status(400)
            self.set_header('content-type', 'application/json')
            self.write(json.dumps(error_data))
            self.finish()
            return

    async def _check_authorization(self) -> Optional[Dict[str, Any]]:
        user_id = self.request.headers.get('X-Real-UserId')

        if self.request.method != 'OPTIONS' and not user_id:
            return {
                'message': 'Ожидаются заголовки X-Real-UserId',
                'errors': [{
                    'message': 'Ожидаются заголовки X-Real-UserId',
                    'code': 'authorizationRequired'
                }],
            }

        return None
