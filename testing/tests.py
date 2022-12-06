import unittest
import requests
s = requests.Session()

class FlaskTest(unittest.TestCase):
   
    def test_register(self):
        data={'firstname':'TestFirst', 
        'lastname':'TestLast',
        'email': 'testemail@gmail.com',
        'password': 'TestPassword11!!',
        'confirmPassword': 'TestPassword11!!' }
        response = s.post("http://127.0.0.1:5000/register", data=data)
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        data={
        'email': 'testemail@gmail.com',
        'password': 'TestPassword11!!',
         }
        response = s.post("http://127.0.0.1:5000/login", data=data)
        self.assertEqual(response.status_code, 200)

    def test_tasks(self):
        response = s.get("http://127.0.0.1:5000/tasks")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual('Title' in response.text and 'Date' in response.text, True)

    def test_task(self):
        if s.get("http://127.0.0.1:5000/tasks/1").status_code == 404:
            self.test_new()
        response = s.get("http://127.0.0.1:5000/tasks/1")
        print(response)
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual('Example Task' in response.text, True)

    def test_new(self):
        self.test_login()
        if s.get("http://127.0.0.1:5000/tasks/1").status_code == 200:
            self.test_delete()
        s.get("http://127.0.0.1:5000/tasks/new")
        response = s.post("http://127.0.0.1:5000/tasks/new", data={'title':'Example Task','taskText':'task description'})
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual(s.get('http://127.0.0.1:5000/tasks/1').status_code, 200)

    def test_edit(self):
        self.test_login()
        if s.get("http://127.0.0.1:5000/tasks/1").status_code == 404:
            self.test_new()
        response = s.post("http://127.0.0.1:5000/tasks/edit/1", data={'title':'Edited Example Task','taskText':'edited task description'})
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_delete(self):
        self.test_login()
        if s.get("http://127.0.0.1:5000/tasks/1").status_code == 404:
            self.test_new()
        response = s.post('http://127.0.0.1:5000/tasks/delete/1/')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual(s.get('http://127.0.0.1:5000/tasks/1').status_code, 404)
    
    def test_comment(self):
        self.test_login()
        if s.get("http://127.0.0.1:5000/tasks/1").status_code == 404:
            self.test_new()
        response = s.post('http://127.0.0.1:5000/tasks/1/comment', data={'comment': 'Test Comment'})
        self.assertEqual(response.status_code, 200)
        response = s.get('http://127.0.0.1:5000/tasks/1')
        self.assertIn('Test Comment', response.text)


if __name__ == " __main__":
    unittest.main()
    
