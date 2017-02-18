from abc import abstractmethod

import colander
import deform
from pyramid.renderers import render
from sqlalchemy.orm import Query
from websauna.compat.typing import Optional
from websauna.compat.typing import List
from websauna.compat.typing import Callable
from websauna.compat.typing import Tuple
from websauna.system.form.csrf import CSRFSchema
from websauna.system.http import Request


class Column:
    """Define listing in a column."""

    header_template = "crud/column_header.html"

    body_template = "crud/column_body.html"

    navigate_view_name = None

    #: Callback get_navigate_url(request, resource) to resolve the link where the item this column should point to
    navigate_url_getter = None

    getter = None

    #: Arrow formatting string
    format = "MM/DD/YYYY HH:mm"

    def __init__(self, id, name=None, renderer=None, header_template=None, body_template=None, getter: Callable=None, format=None, navigate_view_name=None, navigate_url_getter=None):
        """
        :param id: Must match field id on the model
        :param name:
        :param renderer:
        :param header_template:
        :param body_template:
        :param getter: func(view instance, object) - extract value for this column for an object
        :param navigate_url_getter: callback(request, resource) to generate the target URL if the contents of this cell is clicked
        :param navigate_view_name: If set, make this column clickable and navigates to the traversed name. Options are "show", "edit", "delete"
        :return:
        """
        self.id = id
        self.name = name
        self.renderer = renderer
        self.getter = getter

        if format:
            self.format = format

        if header_template:
            self.header_template = header_template

        if body_template:
            self.body_template = body_template

        if navigate_view_name:
            self.navigate_view_name = navigate_view_name

        if navigate_url_getter:
            self.navigate_url_getter = navigate_url_getter

    def get_value(self, view, obj):
        """Extract value from the object for this column.

        Called in listing body.

        :param view: View class calling us
        :param obj: The object we are listing
        """

        if self.getter:
            val = self.getter(view, self, obj)
        else:
            val = getattr(obj, self.id)

        if val is None:
            return ""
        else:
            return val

    def get_navigate_target(self, resource, request):
        """Get URL where clicking the link in the listing should go.

        By default, navigate to "show" view of the resource.
        """
        return resource

    def get_navigate_url(self, resource, request, view_name=None):
        """Get the link where clicking this item should take the user.

        By default, navigate to "show" view of the resource.

        TODO: Switch resource/request argument order.

        :param view_name: Override class's ``navigate_view_name``.
        """

        if self.navigate_url_getter:
            return self.navigate_url_getter(request, resource)

        if not self.navigate_view_name:
            return None

        target = self.get_navigate_target(resource, request)

        if not target:
            return None

        view_name = view_name or self.navigate_view_name

        return request.resource_url(target)


class StringPresentationColumn(Column):
    """Renders the default string presentation of the object.

    You can change the stringify method::

        StringPresentationColumn(formatter=my_func)

    where my_func is callable::

        my_func(value)
    """

    def __init__(self, **kwargs):
        self.formatter = kwargs.pop("formatter", str)
        super(StringPresentationColumn, self).__init__(**kwargs)

    def get_value(self, view, obj):
        """Extract value from the object for this column.

        Called in listing body.
        """
        val = str(obj)
        return self.formatter(val)


class ControlsColumn(Column):
    """Render View / Edit / Delete buttons."""
    def __init__(self, id="controls", name="Actions", header_template="crud/column_header_controls.html", body_template="crud/column_body_controls.html"):
        super(ControlsColumn, self).__init__(id=id, name=name, header_template=header_template, body_template=body_template)


class FriendlyTimeColumn(Column):
    """Print both accurate time and humanized relative time."""
    def __init__(self, id, name, navigate_view_name=None, timezone=None, header_template=None, body_template="crud/column_body_friendly_time.html"):

        if timezone:
            self.timezone = timezone

        super(FriendlyTimeColumn, self).__init__(id=id, name=name, navigate_view_name=navigate_view_name, header_template=header_template, body_template=body_template)


class Table:
    """Describe table columns to a CRUD listing view."""

    def __init__(self, columns: Optional[List[Column]] =None):
        """
        :param columns: List of columns to used to render the list view
        :return:
        """
        self.columns = columns or []

    def get_columns(self):
        return self.columns


class Filter:
    """Filter a list based on criteria."""

    #: Template we use to frame the filter form
    template = "crud/filter.html"

    def __init__(self, **kwargs):
        """
        :param kwargs: Passed as is as instance variables
        """
        self.__dict__.update(kwargs)

    @abstractmethod
    def create_form(self, request, filter_context) -> deform.Form:
        """Create a form that allows set the query parameters."""

    @abstractmethod
    def apply_on_query(self, query: Query, appstruct: dict) -> Query:
        """Get a new listing query that has the filters applied."""

    def process_form(self, request, filter_context) -> dict:
        """Extract incoming HTTP POST from request.

        :raise: deform.ValidationError in the case some of the fields could not be validated

        :return: Colander appstruct dictionary
        """

    def render(self, request: Request, rendered_form: str, filter_context: dict) -> str:
        """Render the filter in the listing view.

        The form is put into a filter decoration template.

        :param form: deform.Form object

        :return: HTML code for the output
        """

        template_content = {
            "filter_context": filter_context,
            "rendered_form": rendered_form,
        }

        html = render(self.template, request=request, context=template_content)
        return html

    def process(self, request: Request, query: Query, filter_context: dict) -> Tuple[Query, str]:
        """Process a filter.

        The filter core action method. Render filter on HTML view. Update query object based on filter parameters.

        :param request:
        :param query:
        :param filter_context: Extra arguments one can pass around for customized templates, etc.
        :return: tuple(updated query object,
        """

        form = self.create_form()

        try:
            appstruct = self.process_form(filter_context)
            rendered_form = form.render(appstruct)
            query = self.apply_on_query(query, appstruct)
        except deform.ValidationFailure as e:
            rendered_form = e

        html = self.render(request, rendered_form, filter_context)

        return query, html


def process_filters(request: Request, filters: List[Filter], query: Query, filter_context: dict) -> Tuple[Query, List[str]]:
    """Process all listing filters.

    :param request: HTTP request
    :param filters: List of filter factories, that take request as argument
    :param query: SQLAlchemy query
    :parma filter_context: Extra context passed to the filters
    :return: (A new query object, List of HTML snippets as string)
    """

    rendered_filters = []
    for f in filters:
        query, html = f.proces(request, query)
        rendered.append(html)

    return query, rendered_filters


