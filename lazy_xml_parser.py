from typing import Tuple, Union, Iterator, List
from xml.etree.ElementTree import XMLPullParser, Element

_chunk_size: int = 1024


def parse(xml_text: Union[bytes, Iterator[bytes]], path: Tuple = ('feed', 'entry')) -> Iterator[Union[dict, str]]:
    """
    lazy parser for large xml to extract a list of embedded xml elements

    :param xml_text: xml input, bytes or an iterator of bytes
    :param path: a tuple specifying the path of the xml elements to extract
    :return an iterator of dicts of the embedded xml elements
    """

    # convert xml_text to bytes iterator if it's of bytes type
    if type(xml_text) is bytes:
        xml_chunks = (xml_text[i:i + _chunk_size] for i in range(0, len(xml_text), _chunk_size))
    else:
        xml_chunks = xml_text

    path: list = list(path)
    tag_stack: [str] = []
    xml_parser = XMLPullParser(events=('start', 'end'))

    handle_partial_xml = _get_partial_xml_handler(path)

    for chunk in xml_chunks:
        xml_parser.feed(chunk)
        for element in handle_partial_xml(xml_parser):
            yield _elem_to_dict_or_str(element)


def _get_partial_xml_handler(path: List[str]):

    element_stack: List[Element] = []

    def _handle(parser: XMLPullParser):
        events = parser.read_events()
        nonlocal element_stack

        for action, elem in events:
            elem: Element
            if action == 'start':
                element_stack.append(elem)
            elif action == 'end':
                last_tag = _simplify(element_stack[-1].tag)
                current_tag = _simplify(elem.tag)
                if last_tag != current_tag:
                    raise Exception('unmatched tag, start: {}, end: {}'.format(last_tag, current_tag))
                if path == list(map(lambda x: _simplify(x.tag), element_stack)):
                    yield elem

                element_stack = element_stack[:-1]
                if len(element_stack) > 0:
                    element_stack[-1].clear()

    return _handle


def _simplify(tag: str) -> str:
    return tag.split('}', 1)[1] if '}' in tag else tag


def _elem_to_dict_or_str(elem: Element) -> Union[dict, str]:
    children = list(iter(elem))
    if len(children) == 0:
        return elem.text
    result = {}
    for child in children:
        child: Element = child
        result[_simplify(child.tag)] = _elem_to_dict_or_str(child)
    return result
