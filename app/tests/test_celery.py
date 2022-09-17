from app.tasks import add, update_txModel
from unittest import TestCase
import pytest

@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
class MyTest(TestCase):
    def test(self):
        assert add.delay(1,2).get(timeout=10) == 3
    
    