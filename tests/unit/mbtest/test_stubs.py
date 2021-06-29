# encoding=utf-8
import logging

from mbtest.imposters import Imposter, InjectionResponse, Stub

logger = logging.getLogger(__name__)


def test_structure_inject():
    expected_imposter = Imposter(
        Stub(responses=InjectionResponse(inject="function (request) {\n}")), port=4546
    )
    imposter_structure = expected_imposter.as_structure()
    imposter = Imposter.from_structure(imposter_structure)
    assert imposter.port == expected_imposter.port
