from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from mongoengine import connect

from positions.models import Positions


class HunterTest(APITestCase):
    client = APIClient()

    def setUp(self):
        self.positions = []
        for i in range(3):
            self.positions.append(Positions.objects.create(
                ad_id=i,
                position=str(i)
            ))

    def tearDown(self):
        db = connect('gogo-test')
        db.drop_database('gogo-test')
        db.close()

    def test_list(self):
        link = '/api/positions/'
        response = self.client.get(link, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Positions.objects.all()), len(response.data))

    def test_delete(self):
        link = '/api/positions/' + str(self.positions[0].id) + '/'
        response = self.client.delete(link)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Positions.objects.all()) + 1, len(self.positions))

    def test_retrieve(self):
        link = '/api/positions/' + str(self.positions[0].id) + '/'
        response = self.client.get(link, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.positions[0].id))

    def test_comment(self):
        link = '/api/positions/' + str(self.positions[0].id) + '/' + 'comment/'
        data = {"comment": "Snowball"}
        response = self.client.put(link, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], data['comment'])

    def test_compare(self):
        link = '/api/positions/' + 'filter/?ids=' + str(self.positions[0].id) + \
            ',' + str(self.positions[1].id)
        print(link)
        response = self.client.get(link, format='json')
        self.assertEqual(len(response.data), 2)
        print(response.data)
        self.assertEqual(response.data[0]['id'], str(self.positions[0].id))
        self.assertEqual(response.data[1]['id'], str(self.positions[1].id))
