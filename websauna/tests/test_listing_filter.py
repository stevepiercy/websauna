"""Test listing filtering."""
import pytest
from websauna.system.crud.listing import process_filters
from websauna.system.crud.sqlalchemy import SingleRelationshipValueFilter
from websauna.system.user.models import User
from websauna.tests.utils import create_user



@pytest.fixture
def list_query(dbsession, registry):
    """Create two users, one in admin users. Return query to query these users."""
    create_user(dbsession, registry, email="u1@example.com", admin=True)
    create_user(dbsession, registry, email="u2@example.com", admin=False)
    return dbsession.query(User)


@pytest.fixture
def sql_relationship_filters(dbsession, registry):
    import pdb ; pdb.set_trace()
    filters = [
        SingleRelationshipValueFilter(column=User.group, title="Choose group")
    ]
    return filters


def test_filter_sqlalchemy_relationship_no_value(test_request, list_query, sql_relationship_filters):
    """Filtering works if no relationship value is selected."""
    query, html_snippets = process_filters(test_request, sql_relationship_filters, list_query, {})
    assert query.count() == 2


def test_filter_sqlalchemy_relationship_one_value():
    """Test """