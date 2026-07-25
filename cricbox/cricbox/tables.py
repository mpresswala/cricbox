from cricbox.utils import balls_to_overs, overs_to_balls

import django_tables2 as tables


class FloatColumn(tables.Column):
    def render(self, value):
        if value is None:
            return value
        return round(value, 2)


class SummingColumn(tables.Column):
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)


class OversColumn(tables.Column):
    """Render a single innings' overs (already valid, e.g. 4.3), whole -> int."""

    def render(self, value):
        return balls_to_overs(overs_to_balls(value))


class CareerOversColumn(tables.Column):
    """Render a career total supplied as a ball count into overs notation."""

    def render(self, value):
        return balls_to_overs(value)


class SummingOversColumn(OversColumn):
    """Sum a column of per-innings overs correctly (by balls) for the footer."""

    def render_footer(self, bound_column, table):
        total_balls = sum(overs_to_balls(bound_column.accessor.resolve(row)) for row in table.data)
        return balls_to_overs(total_balls)
