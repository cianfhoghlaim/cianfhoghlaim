import regex
from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def current_time():
    return timezone.now().isoformat()


@register.simple_tag
def pagexml_points(points):
    return ' '.join(','.join(map(lambda x: str(int(x)), pt)) for pt in points)


@register.simple_tag
def alto_points(points):
    return ' '.join(' '.join(map(lambda x: '%g' % x, pt)) for pt in points)


class Segment():

    def __init__(self, content, graphs):
        self.content = content
        self.graphs = graphs
        self.make_graphs_boxes()

    @property
    def polygon(self):
        polys = [c['poly'] for c in self.graphs]
        return [pt for poly in polys for pt in poly]

    @property
    def box(self):
        return [*map(min, *self.polygon), *map(max, *self.polygon)]

    @property
    def width(self):
        return self.box[2] - self.box[0]

    @property
    def height(self):
        return self.box[3] - self.box[1]

    @property
    def confidence(self):
        return min([c['confidence'] for c in self.graphs])

    def make_graphs_boxes(self):
        # enrich graphs with flattened poly lists
        for graph in self.graphs:
            graph['box'] = [*map(min, *graph['poly']), *map(max, *graph['poly'])]


@register.filter
def group_by_word(graphs):
    # merge the characters
    line = ''.join([c['c'] for c in graphs])
    words = list(filter(None, regex.split('([^\\S]+|\\S+)', line)))
    segments = []
    index = 0
    for word in words:
        segments.append(Segment(word, graphs[index:index + len(word)]))
        index += len(word)
    return segments


@register.filter
def is_whitespace(segment):
    return not regex.match('\\S+', segment.content)


@register.filter
def subtract(val1, val2):
    return val1 - val2
