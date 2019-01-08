from random import randint
from xml.etree import ElementTree

from pytest import fixture

import lazy_xml_parser
import os.path

file_name = "users.xml"
number_of_users = 1000000


@fixture
def xml_file_bytes():
    if not os.path.exists(file_name):
        users = ElementTree.Element("users")
        for i in range(1, number_of_users + 1):
            u = ElementTree.SubElement(users, "user")
            ElementTree.SubElement(u, "name").text = "user" + str(i)
            ElementTree.SubElement(u, "age").text = str(randint(1, 100))
        tree = ElementTree.ElementTree(users)
        tree.write(file_name)
    with open(file_name, 'rb') as f:
        bs = f.read()
    return bs


def test_parse(xml_file_bytes):
    users = lazy_xml_parser.parse(xml_file_bytes, path=('users', 'user'))
    assert number_of_users == sum(1 for _ in users)


