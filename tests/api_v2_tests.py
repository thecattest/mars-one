from requests import get, post, put, delete
from pprint import pprint


def test_link(expected_code, func="users", method="GET", id="0", json={}, print_res=False):
    link = "http://localhost:8000/api/v2/"
    link += func
    if id != "0":
        link += '/' + id

    if method == "GET":
        response = get(link)
    elif method == "POST":
        response = post(link, json=json)
    elif method == "PUT":
        response = put(link, json=json)
    elif method == "DELETE":
        response = delete(link)
    else:
        print("blin")
        return

    if response.status_code == expected_code:
        print(link, "ok")
        if print_res:
            pprint(response.json())
    else:
        print(link)
        print(response.status_code)
        print(response.json())


test_link(200, print_res=True)
test_link(404, id="999")
test_link(404, id="q")
test_link(200, id="1", print_res=True)

test_link(400, method="POST")
test_link(400, method="POST", json={"surname": "aaaa"})
test_link(200, method="POST", json={
    "surname": "A",
    "name": "B",
    "age": 10,
    "position": "Pos",
    "speciality": "Spec",
    "address": "hgfhg",
    "email": "vgvjhjh"
})

test_link(200, print_res=True, id="9")

test_link(405, method="DELETE")
test_link(200, method="DELETE", id="9")

test_link(404, id="9")