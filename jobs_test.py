from requests import get, post, put, delete
from pprint import pprint


def test_link(expected, func="jobs", method="GET", id="0", json={}, print_res=False):
    link = "http://localhost:8000/api/"
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

    if response.status_code == expected:
        print(link, "ok")
        if print_res:
            pprint(response.json())
    else:
        print(link)
        print(response.status_code)
        print(response.json())


# test_link(200, print_res=True)
# test_link(200, id="1", print_res=True)
# test_link(404, id="999")
# test_link(404, id="q")

# test_link(400, method="POST")
# test_link(400, method="POST", json={"job": "test_job"})
test_link(200, method="POST",
          json={
              "job": "test_job",
              "team_leader": 1,
              "work_size": 15,
              "collaborators": "1, 2, 3",
              "kind": "1",
              "is_finished": False})
# не указан id
test_link(400, method="PUT", json={"job": "test"})
# указан неправильный id
test_link(404, method="PUT", json={"id": "999", "job": "test"})

# правильный id
test_link(200, method="PUT", json={"id": "5", "job": "updated test"})
# проверить, что изменилась
test_link(200, print_res=True)

# правильный id
test_link(200, method="PUT", json={"id": "5",
                                   "job": "updated test again",
                                   "work_size": "50",
                                   "collaborators": "4",
                                   "kind": "2",
                                   "team_leader": "2",
                                   "is_finished": True})
# проверить, что изменилась
test_link(200, print_res=True)

# удалим эту работу
# test_link(404, method="DELETE", id="999")
test_link(200, method="DELETE", id="5")