import collections
import dataclasses
import time
from heapq import heapify, heappop, heappush, heappushpop
from typing import Callable, List, Optional

__all__ = ("ScheduledItem", "Scheduler")


def remove(items, func):
    """
    Remove scheduled items with func ``func`` from list
    ``remove_from`` and return True if it was removed

    """
    removed = False
    remove_ = items.remove
    for i in list(i for i in items if i.func is func):
        remove_(i)
        removed = True
    return removed


# after py 3.10, add slots=True
@dataclasses.dataclass()
class ScheduledItem:
    """
    Describes a scheduled callback.

    """

    func: Callable
    last_ts: float
    next_ts: float
    interval: float
    repeat: bool

    def __lt__(self, other):
        try:
            return self.next_ts < other.next_ts
        except AttributeError:
            return self.next_ts < other


class Scheduler:
    """
    Class for scheduling functions.

    Probably not thread safe.

    The function should have a prototype that includes ``dt`` as the
    first argument, which gives the elapsed time, in time units,
    since the last clock tick.

        def callback(dt):
            pass


    Soft Scheduling
    ===============

    Items will be scheduled and rescheduled in such a way to prevent
    several items from running during the same tick.  Enabling a
    "soft" reschedule means that item is tolerant to having the
    interval slightly modified.

    """

    def __init__(self, time_function: Callable = time.perf_counter):
        """
        Initialise a Scheduler, with optional custom time function.

        Parameters:
            time_function: Return the elapsed time

        """
        self._time: Callable = time_function
        self._now: float = 0.0
        self._last_ts: float = 0.0
        self._times = collections.deque(maxlen=10)
        self._scheduled_items: List[ScheduledItem] = list()
        self._next_tick_items: List[ScheduledItem] = list()
        self._current_interval_item: Optional[ScheduledItem] = None
        self.cumulative_time: float = self._last_ts

    def schedule_once(self, func: Callable, delay: float = 0.0, soft: bool = False) -> ScheduledItem:
        """
        Schedule a function to be run once sometime in the future.

        If the delay is not specified, the function will be executed
        during the next tick.

        Parameters:
            func: Function to be called
            delay: Delay in time unit until it is called
            soft: See notes about Soft Scheduling

        Returns:
            Reference to scheduled item.

        """
        return self.schedule(func, delay, 0.0, False, soft)

    def schedule_interval(
        self,
        func: Callable,
        interval: float = 0.0,
        delay: float = 0.0,
        soft: bool = False,
    ):
        """
        Schedule a function to run on an interval.

        NOTE!  If delay==0.0, then the interval will start the next frame,
        meaning, the callback will happen the next tick, and then follow
        the interval.  If you want to avoid this, then set delay to the same
        value as the interval.

        Items are rescheduled after they are executed.  That means that
        by default, the interval of items may not be consistent with
        the initial time with was scheduled.

        If the interval is not specified, the function will be executed
        every time the scheduler is ticked.

        Parameters:
            func: Function to be called
            interval: Repeat on this interval
            delay: Delay in time unit until it is called for first time
            soft: See notes about Soft Scheduling

        Returns:
            Reference to scheduled item

        """
        return self.schedule(func, delay, interval, True, soft)

    def schedule(self, func: Callable, delay: float, interval: float, repeat: bool, soft: bool):
        assert delay >= 0.0
        assert interval >= 0.0
        if interval:
            assert repeat

        last_ts = self._get_nearest_ts()
        if soft:
            assert delay > 0.0
            next_ts = self._get_soft_next_ts(last_ts, delay)
            last_ts = next_ts - delay
        next_ts = last_ts + delay

        item = ScheduledItem(func, last_ts, next_ts, interval, repeat)
        if repeat and (interval == next_ts == 0.0):
            self._next_tick_items.append(item)
            if len(self._next_tick_items) > 10:
                # TODO: warning only!
                raise RuntimeError
        else:
            heappush(self._scheduled_items, item)

        return item

    def unschedule(self, func) -> None:
        """
        Remove a function from the schedule.

        NOTE: do not unschedule own function during function call

        If the function appears in the schedule more than once, all
        occurrences are removed.  If the function was not scheduled,
        no error is raised.

        Parameters:
            func: The function to remove from the schedule.

        """
        remove(self._next_tick_items, func)
        if remove(self._scheduled_items, func):
            heapify(self._scheduled_items)

    def tick(self) -> float:
        """
        Cause clock to update and call scheduled functions.

        This updates the clock's internal measure of time and returns
        the difference since the last update (or since the clock was
        created).

        Will call any scheduled functions that have elapsed.

        Returns:
            The number of time units since the last "tick", or 0 if this
            was the first tick.

        """
        delta_t = self.set_time(self._time())
        self._times.append(delta_t)
        self.call_scheduled_functions(delta_t)
        return delta_t

    def call_scheduled_functions(self, dt: float):
        """
        Call scheduled functions that elapsed on the last `update_time`.

        Parameters:
            dt: The elapsed time since the last update to pass to each
            scheduled function.

        """
        now = self._last_ts

        # handle items scheduled for each tick
        if self._next_tick_items:
            # make copy of list in case event removes itself
            for item in list(self._next_tick_items):
                item.func(dt)

        item = None
        get_soft_next_ts = self._get_soft_next_ts
        scheduled_items = self._scheduled_items
        while scheduled_items:

            # if next item is scheduled in the future then exit
            if scheduled_items[0].next_ts > now:
                break

            # the scheduler will hold onto a reference to an item in
            # case it needs to be rescheduled.  it is more efficient
            # to push and pop the heap in one call than to make two
            # operations.
            if item is None:
                item = heappop(scheduled_items)
            else:
                item = heappushpop(scheduled_items, item)

            # call the function associated with the scheduled item
            item.func(now - item.last_ts)

            if item.repeat:
                item.next_ts = item.last_ts + item.interval
                item.last_ts = now

                # the execution time of this item has already passed,
                # so it must be rescheduled
                if item.next_ts <= now:
                    if now - item.next_ts < 0.05:
                        # reschedule
                        item.next_ts = now + item.interval
                    else:
                        # missed by significant amount; soft reschedule
                        # to avoid lumping everything together. in this
                        # case, the next dt will not be accurate.
                        item.next_ts = get_soft_next_ts(now, item.interval)
                        item.last_ts = item.next_ts - item.interval

            else:
                # this item will not be rescheduled
                item = None

        if item:
            heappush(scheduled_items, item)

    def get_running_time(self) -> float:
        """
        Get time clock has been running

        """
        return self.cumulative_time

    def get_counter(self) -> float:
        """
        Get internal counter value

        """
        return self._last_ts

    def get_interval(self) -> float:
        """
        Get the average amount of time passed between each tick.

        Useful for calculating FPS if this clock is used with the
        display.  Returned value is averaged from last 10 ticks.

        Value will be 0.0 if before 1st tick.

        Returns:
            Average amount of time passed between each tick

        """
        try:
            return sum(self._times) / len(self._times)
        except ZeroDivisionError:
            return 0.0

    def get_schedule(self) -> List[ScheduledItem]:
        """
        Return copy of the schedule.

        """
        return self._next_tick_items + sorted(self._scheduled_items)

    def set_time(self, time_stamp: float) -> float:
        """
        Set the clock manually and do not call scheduled functions.

        Parameters:
            time_stamp: This will become the new value of the clock.

        Returns:
            The number of time units since the last update, or 0.0 if
            this was the first update.

        """
        time_stamp = float(time_stamp)
        # self._last_ts will be -1 before first time set
        if self._last_ts < 0:
            delta_t = 0.0
        else:
            delta_t = time_stamp - self._last_ts
        self.cumulative_time += delta_t
        self._last_ts = time_stamp
        return delta_t

    def get_idle_time(self) -> Optional[float]:
        """
        Get the time until the next item is scheduled.

        Returns:
            Time until the next scheduled event in time units, or
            ``None`` if there is no events scheduled.

        """
        if self._next_tick_items:
            return 0.0

        try:
            next_ts = self._scheduled_items[0].next_ts
            return max(next_ts - self._time(), 0.0)
        except IndexError:
            return None

    def _get_nearest_ts(self):
        """
        Schedule from now, unless now is sufficiently close to last_ts,
        in which case use last_ts.  This clusters together scheduled
        items that probably want to be scheduled together.
        """
        last_ts = self._last_ts
        ts = self._time()
        if ts - last_ts > 0.2:
            last_ts = ts
        return last_ts

    def _get_soft_next_ts(self, last_ts, interval):
        def taken(ts, e):
            """Return True if the given time has already got an item
            scheduled nearby.
            """
            for item in self._scheduled_items:
                if item.next_ts is None:
                    continue
                elif abs(item.next_ts - ts) <= e:
                    return True
                elif item.next_ts > ts + e:
                    return False
            return False

        next_ts = last_ts + interval
        if not taken(next_ts, interval / 4):
            return next_ts

        dt = interval
        divs = 1
        while True:
            next_ts = last_ts
            for i in range(divs - 1):
                next_ts += dt
                if not taken(next_ts, dt / 4.0):
                    return next_ts
            dt /= 2
            divs *= 2

            # Avoid infinite loop in pathological case
            if divs > 16:
                return next_ts
