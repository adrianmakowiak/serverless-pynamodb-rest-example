from datetime import datetime
from unittest import TestCase
import os
import uuid

from pynamodb.exceptions import DoesNotExist

from todos.todo_model import TodoModel


class TestIntegrationBase(TestCase):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def setUp(self, load_dbs=None):
        TodoModel.setup_model(TodoModel, 'region', 'todo' + str(uuid.uuid1()), 'ENVIRONMENT' not in os.environ)
        if not TodoModel.exists():
            TodoModel.create_table(wait=True)
        if load_dbs:
            for db_file in load_dbs:
                TodoModel.load(db_file)
        super().setUp()

    def tearDown(self):
        if TodoModel.exists():
            TodoModel.delete_table()
        super().tearDown()


class TestTodoModelIntegration(TestIntegrationBase):
    def test_create(self):
        todo_text = 'text'
        todo_id = str(uuid.uuid1())
        t1 = TodoModel(todo_id=todo_id,
                       text=todo_text,
                       created_at=datetime.now())
        t1.save()
        self.assertEquals(t1.text, todo_text)
        self.assertEquals(t1.checked, False)
        t2 = TodoModel.get(hash_key=todo_id)
        self.assertEquals(t2.text, todo_text)
        r = [result for result in TodoModel.scan()]
        self.assertEquals(len(r), 1)
        self.assertEquals(r[0].text, todo_text)
        self.assertEquals(r[0].todo_id, todo_id)
        t2.delete()


class TestTodoModelCreateIntegration(TestIntegrationBase):
    def test_create(self):
        todo_text = 'text'
        todo_id = str(uuid.uuid1())
        t1 = TodoModel(todo_id=todo_id,
                       text=todo_text,
                       created_at=datetime.now())
        t1.save()
        self.assertEquals(t1.text, todo_text)
        self.assertEquals(t1.checked, False)

        # get and check
        t2 = TodoModel.get(todo_id)
        self.assertEquals(t2.text, todo_text)


class TestTodoModelGetIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        super().setUp(load_dbs=[os.path.join(self.dir_path, 'fixtures/todo_db_0.json')])

    def test_get(self):
        found_todo = TodoModel.get('d490d766-8b60-11e7-adba-e0accb8996e6')
        self.assertEquals(found_todo.text, 'text of d490d766-8b60-11e7-adba-e0accb8996e6')

    def test_get_failed(self):
        with self.assertRaises(DoesNotExist):
            TodoModel.get('d490d766-8b60-11e7-adba-e0accb8996e6a')


class TestTodoModelDeleteIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        super().setUp(load_dbs=[os.path.join(dir_path, 'fixtures/todo_db_0.json')])

    def test_delete(self):
        found_todo = TodoModel.get('d490d766-8b60-11e7-adba-e0accb8996e6')
        self.assertEquals(found_todo.text, 'text of d490d766-8b60-11e7-adba-e0accb8996e6')
        found_todo.delete()
        with self.assertRaises(DoesNotExist):
            TodoModel.get('d490d766-8b60-11e7-adba-e0accb8996e6')


class TestTodoModelScanIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        super().setUp(load_dbs=[os.path.join(self.dir_path, 'fixtures/todo_db_0.json')])

    def test_delete(self):
        found_todos = TodoModel.scan()
        todos = [result for result in found_todos]
        self.assertEquals(len(todos), 1)
        self.assertEquals(todos[0].text, 'text of d490d766-8b60-11e7-adba-e0accb8996e6')
        self.assertEquals(todos[0].todo_id, 'd490d766-8b60-11e7-adba-e0accb8996e6')


class TestTodoModelUpdateIntegration(TestIntegrationBase):
    def setUp(self, load_dbs=None):
        super().setUp(load_dbs=[os.path.join(self.dir_path, 'fixtures/todo_db_0.json')])

    def test_update(self):
        found_todo = TodoModel.get('d490d766-8b60-11e7-adba-e0accb8996e6')
        self.assertEquals(found_todo.text, 'text of d490d766-8b60-11e7-adba-e0accb8996e6')
        new_text = 'New text of item'
        found_todo.update({'text': {'action': 'put',
                                    'value': new_text}})
        self.assertEquals(found_todo.text, new_text)

        # refresh and check
        found_todo.refresh()
        self.assertEquals(found_todo.text, new_text)

        # Get and check
        check_text = TodoModel.get('d490d766-8b60-11e7-adba-e0accb8996e6')
        self.assertEquals(check_text.text, new_text)
