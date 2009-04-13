import datetime
import os

from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from schedule.forms import GlobalSplitDateTimeWidget
from schedule.models import Event, Rule, Occurrence, Calendar
from schedule.periods import Period, Month, Day
from schedule.utils import EventListManager

class TestEvent(TestCase):
    def setUp(self):
        rule = Rule(frequency = "WEEKLY")
        rule.save()
        cal = Calendar(name="MyCal")
        cal.save()
        self.recurring_data = {
                'title': 'Recent Event',
                'start': datetime.datetime(2008, 1, 5, 8, 0),
                'end': datetime.datetime(2008, 1, 5, 9, 0),
                'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
                'rule': rule,
                'calendar': cal
               }
        self.data = {
                'title': 'Recent Event',
                'start': datetime.datetime(2008, 1, 5, 8, 0),
                'end': datetime.datetime(2008, 1, 5, 9, 0),
                'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
                'calendar': cal
               }
        
        
    def test_recurring_event_get_occurrences(self):
        recurring_event = Event(**self.recurring_data)
        occurrences = recurring_event.get_occurrences(start=datetime.datetime(2008, 1, 12, 0, 0),
                                    end=datetime.datetime(2008, 1, 20, 0, 0))
        self.assertEquals(["%s to %s" %(o.start, o.end) for o in occurrences],
            ['2008-01-12 08:00:00 to 2008-01-12 09:00:00', '2008-01-19 08:00:00 to 2008-01-19 09:00:00'])
    
    def test_event_get_occurrences_after(self):
        recurring_event=Event(**self.recurring_data)
        recurring_event.save()
        occurrences = recurring_event.get_occurrences(start=datetime.datetime(2008, 1, 5),
            end = datetime.datetime(2008, 1, 6))
        occurrence = occurrences[0]
        occurrence2 = recurring_event.occurrences_after(datetime.datetime(2008,1,5)).next()
        self.assertEqual(occurrence, occurrence2)
    
    def test_get_occurrence(self):
        event = Event(**self.recurring_data)
        event.save()
        occurrence = event.get_occurrence(datetime.datetime(2008, 1, 5, 8, 0))
        self.assertEqual(occurrence.start, datetime.datetime(2008,1,5,8))
        occurrence.save()
        occurrence = event.get_occurrence(datetime.datetime(2008, 1, 5, 8, 0))
        self.assertTrue(occurrence.pk is not None)


class TestOccurrence(TestCase):
    def setUp(self):
        rule = Rule(frequency = "WEEKLY")
        rule.save()
        cal = Calendar(name="MyCal")
        cal.save()
        self.recurring_data = {
                'title': 'Recent Event',
                'start': datetime.datetime(2008, 1, 5, 8, 0),
                'end': datetime.datetime(2008, 1, 5, 9, 0),
                'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
                'rule': rule,
                'calendar': cal
               }
        self.data = {
                'title': 'Recent Event',
                'start': datetime.datetime(2008, 1, 5, 8, 0),
                'end': datetime.datetime(2008, 1, 5, 9, 0),
                'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
                'calendar': cal
               }
        self.recurring_event = Event(**self.recurring_data)
        self.recurring_event.save()
        self.start = datetime.datetime(2008, 1, 12, 0, 0)
        self.end = datetime.datetime(2008, 1, 27, 0, 0)
    
    def test_presisted_occurrences(self):
        occurrences = self.recurring_event.get_occurrences(start=self.start,
                                    end=self.end)
        persisted_occurrence = occurrences[0]
        persisted_occurrence.save()
        occurrences = self.recurring_event.get_occurrences(start=self.start,
                                    end=self.end)
        self.assertTrue(occurrences[0].pk)
        self.assertFalse(occurrences[1].pk)
    
    def test_moved_occurrences(self):
        occurrences = self.recurring_event.get_occurrences(start=self.start,
                                    end=self.end)
        moved_occurrence = occurrences[1]
        moved_occurrence.move(moved_occurrence.start+datetime.timedelta(hours=2),
                              moved_occurrence.end+datetime.timedelta(hours=2))
        occurrences = self.recurring_event.get_occurrences(start=self.start,
                                    end=self.end)
        self.assertTrue(occurrences[1].moved)
    
    def test_cancelled_occurrences(self):
        occurrences = self.recurring_event.get_occurrences(start=self.start,
                                    end=self.end)
        cancelled_occurrence = occurrences[2]
        cancelled_occurrence.cancel()
        occurrences = self.recurring_event.get_occurrences(start=self.start,
                                    end=self.end)
        self.assertTrue(occurrences[2].cancelled)
        cancelled_occurrence.uncancel()
        occurrences = self.recurring_event.get_occurrences(start=self.start,
                                    end=self.end)
        self.assertFalse(occurrences[2].cancelled)
        
