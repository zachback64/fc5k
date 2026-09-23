import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from course_workshop import distance,length,trim


class CourseTest(unittest.TestCase):
    def test_every_option_is_5000_meters_from_the_house(self):
        data=json.loads((ROOT/'data/course-workshop.json').read_text())
        self.assertEqual(len(data['routes']),6)
        for course in data['routes']:
            with self.subTest(course=course['id']):
                self.assertAlmostEqual(length(course['shape']),5000,places=2)
                self.assertLess(distance(course['start'],data['home']),.01)
                self.assertLess(distance(course['finish'],data['home']),260)
                self.assertEqual(course['finish'],course['shape'][-1])
                for marker in course['markers']:
                    self.assertLess(distance(marker['point'],trim(course['shape'],marker['km']*1000)[-1]),.01)

    def test_out_and_backs_return_home_and_turn_at_halfway(self):
        data=json.loads((ROOT/'data/course-workshop.json').read_text())
        courses=[c for c in data['routes'] if c['turnaround']]
        self.assertEqual(len(courses),2)
        for c in courses:
            self.assertEqual(c['start'],c['finish'])
            self.assertLess(distance(c['turnaround'],trim(c['shape'],2500)[-1]),.01)

    def test_trim_refuses_to_invent_distance(self):
        with self.assertRaises(ValueError):
            trim([[41,-87],[41.001,-87]],5000)


if __name__=='__main__':unittest.main()
