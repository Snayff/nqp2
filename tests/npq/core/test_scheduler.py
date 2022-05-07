import unittest
from unittest import mock
from unittest.mock import call

from nqp.core.scheduler import Scheduler


raise unittest.SkipTest("Needs attention.  Skipping for now")


class ClockTestCase(unittest.TestCase):
    """
    Test clock using dummy timekeeper

    """

    def setUp(self):
        self.interval = 1
        self.time = 0
        self.callback_a = mock.Mock()
        self.callback_b = mock.Mock()
        self.callback_c = mock.Mock()
        self.callback_d = mock.Mock()
        self.clock = Scheduler(time_function=lambda: self.time)

    def advance_clock(self, dt=1000):
        """simulate the passage of time like a real clock would"""
        frames = 0
        while self.time < dt:
            frames += 1
            self.time += self.interval
            self.clock.tick()
        return frames

    def test_counter_at_zero(self):
        self.assertEqual(0, self.clock.get_counter())

    def test_counter_single_tick(self):
        self.time = 1.0
        self.clock.tick()
        self.assertEqual(1.0, self.clock.get_counter())

    def test_counter_many_tick_no_advance(self):
        self.clock.tick()
        self.clock.tick()
        self.assertEqual(0.0, self.clock.get_counter())

    def test_counter_many_tick_advance(self):
        self.assertEqual(0, self.clock.tick())
        self.time = 1.0
        self.assertEqual(1.0, self.clock.tick())
        self.time = 2.0
        self.assertEqual(1.0, self.clock.tick())
        self.time = 3.0
        self.assertEqual(1.0, self.clock.tick())
        self.assertEqual(3.0, self.clock.get_counter())

    def test_schedule_once_adds_to_schedule(self):
        self.clock.schedule_once(self.callback_a)
        items = self.clock.get_schedule()
        self.assertEqual(1, len(items))
        self.assertEqual(0, len(self.clock._next_tick_items))

    def test_schedule_interval_adds_to_schedule(self):
        self.clock.schedule_interval(self.callback_a, 1)
        items = self.clock.get_schedule()
        self.assertEqual(1, len(items))
        self.assertEqual(0, len(self.clock._next_tick_items))

    def test_schedule_once_correct_scheduled_item(self):
        self.clock.schedule_once(self.callback_a)
        items = self.clock.get_schedule()
        self.assertEqual(self.callback_a, items[0].func)
        self.assertEqual(False, items[0].repeat)
        self.assertEqual(0.0, items[0].interval)
        self.assertEqual(0.0, items[0].last_ts)

    def test_schedule_interval_correct_scheduled_item(self):
        self.clock.schedule_interval(self.callback_a, 10)
        items = self.clock.get_schedule()
        self.assertEqual(self.callback_a, items[0].func)
        self.assertEqual(True, items[0].repeat)
        self.assertEqual(10.0, items[0].interval)
        self.assertEqual(0.0, items[0].last_ts)
        self.assertEqual(0.0, items[0].next_ts)

    def test_schedule_once_no_delay(self):
        self.clock.schedule_once(self.callback_a)
        self.advance_clock(1000)
        self.assertEqual(1, self.callback_a.call_count)
        self.callback_a.assert_called_once_with(1.0)

    def test_schedule_interval_no_delay(self):
        self.clock.schedule_interval(self.callback_a, 1)
        items = self.clock.get_schedule()
        self.advance_clock(1)
        self.assertEqual(2, items[0].next_ts)
        self.assertEqual(1, items[0].last_ts)
        self.assertEqual(1, self.callback_a.call_count)

    def test_schedule_once_delay(self):
        self.clock.schedule_once(self.callback_a, delay=10)
        items = self.clock.get_schedule()
        self.assertEqual(10, items[0].next_ts)
        self.advance_clock(10)
        self.assertEqual(1, self.callback_a.call_count)
        self.callback_a.assert_called_once_with(10)

    def test_schedule_interval_delay(self):
        self.clock.schedule_interval(self.callback_a, interval=1, delay=2)
        items = self.clock.get_schedule()
        self.assertEqual(1, items[0].interval)
        self.assertEqual(2, items[0].next_ts)

    def test_schedule_interval_callbacks(self):
        self.clock.schedule_interval(self.callback_a, 10)
        self.advance_clock(100)
        self.assertEqual(10, self.callback_a.call_count)
        self.assertEqual([call(10)] * 10, self.callback_a.call_args_list)

    def test_schedule_interval_each_tick(self):
        self.clock.schedule_interval(self.callback_a)

        items = self.clock.get_schedule()
        self.assertEqual(1, len(items))
        self.assertEqual(True, items[0].repeat)
        self.assertEqual(0.0, items[0].interval)
        self.assertEqual(self.callback_a, items[0].func)
        self.assertEqual(self.clock.get_counter(), items[0].next_ts)
        self.assertEqual(self.clock.get_counter(), items[0].last_ts)

        frames = self.advance_clock()
        self.assertEqual(frames, self.callback_a.call_count)

    def test_schedule_once_multiple(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.schedule_once(self.callback_b, 2)
        self.advance_clock(2)
        self.assertEqual(1, self.callback_a.call_count)
        self.assertEqual(1, self.callback_b.call_count)

    def test_schedule_interval_multiple(self):
        # 0, 1, 2
        self.clock.schedule_interval(self.callback_a, 1000)
        self.clock.schedule_interval(self.callback_b, 1000)
        self.advance_clock(2000)
        self.assertEqual(3, self.callback_a.call_count)
        self.assertEqual(3, self.callback_b.call_count)

    def test_schedule_once_unschedule(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.advance_clock()
        self.assertEqual(0, self.callback_a.call_count)

    def test_schedule_interval_unschedule(self):
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.advance_clock()
        self.assertEqual(0, self.callback_a.call_count)

    def test_unschedule_removes_all(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.schedule_interval(self.callback_b)
        self.clock.unschedule(self.callback_a)
        frames = self.advance_clock(10)
        self.assertEqual(0, self.callback_a.call_count)
        # callback_b is used to verify that then event queue was not cleared
        self.assertEqual(frames, self.callback_b.call_count)

    def test_schedule_will_not_call_function(self):
        self.clock.schedule_once(self.callback_a, 0)
        self.assertEqual(0, self.callback_a.call_count)
        self.clock.schedule_interval(self.callback_a, 1)
        self.assertEqual(0, self.callback_a.call_count)

    def test_unschedule_will_not_call_function(self):
        self.clock.schedule_once(self.callback_a, 0)
        self.clock.unschedule(self.callback_a)
        self.assertEqual(0, self.callback_a.call_count)
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.assertEqual(0, self.callback_a.call_count)
        self.assertEqual(0, self.callback_a.call_count)

    def test_unschedule_will_not_fail_if_already_unscheduled(self):
        self.clock.schedule_once(self.callback_a, 0)
        self.clock.unschedule(self.callback_a)
        self.clock.unschedule(self.callback_a)
        self.clock.schedule_interval(self.callback_a, 1)
        self.clock.unschedule(self.callback_a)
        self.clock.unschedule(self.callback_a)

    @unittest.skip("Requires changes to the clock")
    def test_call_sched_return_True_if_called_functions_interval(self):
        self.clock.schedule_once(self.callback_a, 1)
        self.assertFalse(self.clock.call_scheduled_functions(0))
        self.clock.set_time(1)
        self.assertTrue(self.clock.call_scheduled_functions(0))

    def test_tick_return_last_delta(self):
        self.assertEqual(0, self.clock.tick())
        self.time = 1
        self.assertEqual(1, self.clock.tick())
        self.time = 3
        self.assertEqual(2, self.clock.tick())

    @unittest.skip("Requires changes to the clock")
    def test_get_idle_time_None_if_no_items(self):
        self.assertIsNone(self.clock.get_idle_time())

    @unittest.skip("Requires changes to the clock")
    def test_get_idle_time_can_sleep(self):
        self.clock.schedule_once(self.callback_a, 3)
        self.clock.schedule_once(self.callback_b, 1)
        self.clock.schedule_once(self.callback_c, 6)
        self.clock.schedule_once(self.callback_d, 7)
        self.assertEqual(1, self.clock.get_idle_time())
        self.advance_clock()
        self.assertEqual(2, self.clock.get_idle_time())
        self.advance_clock(2)
        self.assertEqual(3, self.clock.get_idle_time())
        self.advance_clock(3)
        self.assertEqual(1, self.clock.get_idle_time())

    @unittest.skip("Requires changes to the clock")
    def test_get_idle_time_cannot_sleep(self):
        self.clock.schedule(self.callback_a)
        self.clock.schedule_once(self.callback_b, 1)
        self.assertEqual(0, self.clock.get_idle_time())

    @unittest.skip
    def test_schedule_item_during_tick(self):
        def replicating_event(dt):
            self.clock.schedule(replicating_event)
            counter()

        counter = mock.Mock()
        self.clock.schedule(replicating_event)

        # one tick for the original event
        self.clock.tick()
        self.assertEqual(1, counter.call_count)
        self.assertEqual(2, len(self.clock.get_schedule()))

        # one tick from original, then two for new
        # now event queue should have two items as well
        self.clock.tick()
        self.assertEqual(3, counter.call_count)
        self.assertEqual(4, len(self.clock.get_schedule()))

    def test_unschedule_interval_item_during_tick(self):
        def suicidal_event(dt):
            counter()
            self.clock.unschedule(suicidal_event)

        counter = mock.Mock()
        self.clock.schedule_interval(suicidal_event, 1)
        self.advance_clock(10)
        self.assertEqual(1, counter.call_count)

    @unittest.skip
    def test_schedule_interval_item_during_tick(self):
        def replicating_event(dt):
            self.clock.schedule_interval(replicating_event, 1)
            counter()

        counter = mock.Mock()
        self.clock.schedule_interval(replicating_event, 1)

        # advance time for the original event
        self.advance_clock()
        self.assertEqual(1, counter.call_count)

        self.assertEqual(2, len(self.clock.get_schedule()))

        # one tick from original, then two for new
        # now event queue should have two items as well
        self.advance_clock()
        self.assertEqual(3, counter.call_count)

        self.assertEqual(4, len(self.clock.get_schedule()))

    def test_scheduler_integrity(self):
        """most tests in this suite do not care about which order
        scheduled items are executed.  this test will verify that
        the order things are executed is correct.
        """
        expected_order = [self.callback_a, self.callback_b, self.callback_c, self.callback_d]

        # schedule backwards to verify that they are scheduled correctly,
        # even if scheduled out-of-order.
        for delay, func in reversed(list(enumerate(expected_order, start=1))):
            self.clock.schedule_once(func, delay)

        for index, func in enumerate(expected_order, start=1):
            self.advance_clock()
            self.assertTrue(func.called)
            self.assertFalse(any(i.called for i in expected_order[index:]))

    def test_slow_clock(self):
        """
        Scheduler will not make up for lost time.  in this case, the
        interval scheduled for callback_[bcd] is 1, and 2 seconds have
        passed. since it won't make up for lost time, they are only
        called once.
        """
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.schedule_interval(self.callback_b, 1)

        # simulate a slow clock
        self.clock.tick()
        self.time = 2
        self.clock.tick()

        self.assertEqual(1, self.callback_a.call_count)
        self.assertEqual(1, self.callback_b.call_count)

    def test_slow_clock_reschedules(self):
        """
        Scheduler will not make up for lost time.  in this case, the
        interval scheduled for callback_[bcd] is 1, and 2 seconds have
        passed. since it won't make up for lost time, they are only
        called once.  this test verifies that missed events are
        rescheduled and executed later
        """
        self.clock.schedule_once(self.callback_a, 1)
        self.clock.schedule_interval(self.callback_b, 1)

        # simulate slow clock
        self.clock.tick()
        self.time = 2
        self.clock.tick()

        # simulate a proper clock (advance clock time by one)
        frames = self.advance_clock()

        # make sure our clock is at 3 seconds
        self.assertEqual(3, self.time)

        # the +1 is the call during the slow clock period
        self.assertEqual(frames + 1, self.callback_a.call_count)

        # only scheduled to happen once
        self.assertEqual(1, self.callback_b.call_count)

        # 2 because they 'missed' a call when the clock lagged
        # with a good clock, this would be 3
        self.assertEqual(2, self.callback_c.call_count)
        self.assertEqual(2, self.callback_d.call_count)

    @unittest.skip("Requires changes to the clock")
    def test_get_interval(self):
        self.assertEqual(0, self.clock.get_interval())
        self.advance_clock(100)
        self.assertEqual(self.interval, round(self.clock.get_interval(), 10))

    def test_soft_scheduling_stress_test(self):
        """test that the soft scheduler is able to correctly soft-schedule
        several overlapping events.
        this test delves into implementation of the clock, and may break
        """
        # this value represents evenly scheduled items between 0 & 1
        # and what is produced by the correct soft-scheduler
        expected = [
            0.0625,
            0.125,
            0.1875,
            0.25,
            0.3125,
            0.375,
            0.4375,
            0.5,
            0.5625,
            0.625,
            0.6875,
            0.75,
            0.8125,
            0.875,
            0.9375,
            1,
        ]

        for i in range(16):
            self.clock.schedule_interval(None, 1, soft=True)

        # sort the clock items
        items = sorted(i.next_ts for i in self.clock.get_schedule())

        self.assertEqual(expected, items)
