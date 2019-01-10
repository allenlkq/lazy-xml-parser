from random import randint
from xml.etree import ElementTree
from pytest import fixture
import lazy_xml_parser
import os.path

file_name_simple = "users_simple.xml"
number_of_users = 1000000

file_name_complex = "users_complex.xml"
number_of_groups = 3
number_of_users_per_group = 5


@fixture
def simple_xml_file_bytes():
    if not os.path.exists(file_name_simple):
        users = ElementTree.Element("users")
        for i in range(1, number_of_users + 1):
            u = ElementTree.SubElement(users, "user")
            ElementTree.SubElement(u, "name").text = "user" + str(i)
            ElementTree.SubElement(u, "age").text = str(randint(1, 100))
        tree = ElementTree.ElementTree(users)
        tree.write(file_name_simple)

    with open(file_name_simple, 'rb') as f:
        bs = f.read()
    return bs


@fixture
def complex_xml_file_bytes():
    if not os.path.exists(file_name_complex):
        groups = ElementTree.Element("groups")
        for i in range(1, number_of_groups + 1):
            users = ElementTree.SubElement(groups, "users")
            for j in range(1, number_of_users_per_group + 1):
                u = ElementTree.SubElement(users, "user")
                ElementTree.SubElement(u, "name").text = "user" + str((i-1) * number_of_users_per_group + j)
                ElementTree.SubElement(u, "age").text = str(randint(1, 100))
        tree = ElementTree.ElementTree(groups)
        tree.write(file_name_complex)
    with open(file_name_complex, 'rb') as f:
        bs = f.read()
    return bs


def test_parse_simple(simple_xml_file_bytes):
    users = lazy_xml_parser.parse(simple_xml_file_bytes, path=('users', 'user'))
    assert number_of_users == sum(1 for _ in users)


def test_parse_complex(complex_xml_file_bytes):
    users = lazy_xml_parser.parse(complex_xml_file_bytes, path=('groups', 'users', 'user'))
    assert number_of_groups * number_of_users_per_group == sum(1 for _ in users)


