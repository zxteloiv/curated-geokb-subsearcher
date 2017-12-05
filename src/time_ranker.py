# coding: utf-8

import re, datetime, time


class TimeRanker(object):
    def __init__(self, time_spec):
        self.time_list = []
        date_modifiers = self.date_modifiers()
        for timepat in self.time_patterns():
            for m in re.finditer(timepat, time_spec):
                # add (modifier, start time, end time) to time_list
                modifier, start_time, end_time = m.group(1), m.group(2), m.group(3)
                for key, action in date_modifiers:
                    if key in modifier:
                        self.time_list.append((action, start_time, end_time))
                        break
                    else:
                        pass
                else:
                    # no modifier is recognized for this time span,
                    # it then means EVERY kind of day the time span is correct
                    self.time_list.append(('every', start_time, end_time))

        # no time span is found in shop spec, perhaps it says
        # it will be open for business at ANY time
        if len(self.time_list) == 0:
            for exp in self.unlimited_exps():
                if exp in time_spec:
                    self.time_list = [("any", None, None)]
                    break

    def rank_against(self, time_utterance, today=None):
        """
        give a ranking score for the (time spec, time utter) pair,
        input:
            time_utterance, the substring of natural utterance specifying time
            today, a datetime.datetime class indicating the current time
        :return a score either 0 if not matched, 1 otherwise
        """
        for (modifier, starts, ends) in self.time_list:
            if not self._modifier_match(time_utterance, modifier, today):
                continue

            if modifier == 'any':
                return 1

            # the modifier in shop spec. matches the utterance, now check the time span
            if self._match_timespan(time_utterance, starts, ends, today):
                return 1

        return 0

    @staticmethod
    def _modifier_match(time_utterance, modifier, today=None):
        if modifier in ('every', 'any'):
            return True

        # compute day of week if required implicitly in time utterance
        dayofweek = None
        dynamic_dates = [u'现在', u'今天']
        if any(TimeRanker.general_match(x, time_utterance) for x in dynamic_dates):
            today = datetime.datetime.now() if today is None else today
            dayofweek = today.isoweekday()

        # check if day of week is workday if available,
        # otherwise match workday pattern in utterance directly
        if modifier == 'workdays':
            if dayofweek is not None:
                return dayofweek in xrange(1, 6)

            workday_keywords = [re.compile(u'周[一二三四五]'), u'工作日']
            return any(TimeRanker.general_match(x, time_utterance) for x in workday_keywords)

        # check if day of week is weekend if available
        # otherwise match weekend pattern in utterance directly
        if modifier == 'weekends':
            if dayofweek is not None:
                return dayofweek in [6, 7]

            weekend_keywords = [re.compile(u'周六|周日|周末'), u'节假日']
            return any(TimeRanker.general_match(x, time_utterance) for x in weekend_keywords)

        # do not consider other types of modifiers now, just use the time span
        # specified by the modifier afterwards
        return True

    @staticmethod
    def _match_timespan(time_utterance, starts, ends, today=None):
        """
        check if time utterance talks about a time between the span
        :return True if the time is within the time span, otherwise False is returned
        """
        starts = datetime.datetime.strptime(starts, "%H:%M")
        ends = datetime.datetime.strptime(ends, "%H:%M")

        if today is not None:
            return starts.hour <= today.hour <= ends.hour

        am_modifier = [u'早上', u'半夜', u'中午']
        pm_modifier = [u'下午', u'晚上']
        m = re.search(u'((二?十)?[一二三四五六七八九])点', time_utterance)
        hour = TimeRanker.parse_chn_hour_num(m.group(1)) if m else None
        if hour is None:
            m = re.search(u'(\d+)点', time_utterance)
            hour = int(m.group(1)) if m else None

        if any(TimeRanker.general_match(x, time_utterance) for x in am_modifier):
            hour %= 12
        elif any(TimeRanker.general_match(x, time_utterance) for x in pm_modifier):
            hour = (hour % 12) + 12
        else:
            hour %= 24

        return starts.hour <= hour <= ends.hour

    @staticmethod
    def parse_chn_hour_num(chn_hour_utterance):
        hour = 0
        for char in list(chn_hour_utterance):
            hour += u'一二三四五六七八九十'.find(char) + 1

        if u'二十' in chn_hour_utterance:
            hour += 8   # 二十二 should be 22 but is actually 10 + 2 + 2 for the time being
        return hour

    @staticmethod
    def date_modifiers():
        """return a list of date modifiers that may occur in database"""
        return [
            # generally the more specific modifiers are placed ahead, by priority
            (u"每天", "every"), (u"周一至周日", "every"), (u"周一-周日", "every"),

            (u"周一至周五", "workdays"), (u"周一-周五", "workdays"),

            (u"工作日", "workdays"),
            (u"节假日", "weekends"),

            (u"周末", "weekends"), (u"周六", "weekends"), (u"周日", "weekends"),

            (u"上午", "every"), (u"下午", "every"), (u"晚上", "every"), (u"夜间", "every"),
        ]

    @staticmethod
    def time_patterns():
        return [
            # anything : 9:00 - 21:00
            re.compile(r'([^:]*?):?(\d\d?:\d\d)[^\d]{,2}-[^\d]{,2}(\d\d?:\d\d)'),
        ]

    @staticmethod
    def unlimited_exps():
        return [ u'24小时', u'每天', u'全天', ]

    @staticmethod
    def general_match(pattern, string):
        RE_TYPE = type(re.compile(u're'))
        if isinstance(pattern, RE_TYPE):
            return pattern.search(string)

        return pattern in string


if __name__ == "__main__":
    print 'required: 1 1 1 0'
    ranker = TimeRanker(u'周一至周日- - :9:00-21:00')
    print ranker.rank_against(u'工作日早上九点')
    print ranker.rank_against(u'节假日早上9点')
    print ranker.rank_against(u'节假日二十一点')
    print ranker.rank_against(u'周三半夜2点')

    print 'required: 1 1 1 0'
    ranker = TimeRanker(u' - - :9:00-21:00')
    print ranker.rank_against(u'工作日早上九点')
    print ranker.rank_against(u'节假日早上9点')
    print ranker.rank_against(u'节假日二十一点')
    print ranker.rank_against(u'周三半夜2点')

    print 'required: 1 1 1 0'
    ranker = TimeRanker(u'每天 - - :9:00-21:00')
    print ranker.rank_against(u'工作日早上九点')
    print ranker.rank_against(u'节假日早上9点')
    print ranker.rank_against(u'节假日二十一点')
    print ranker.rank_against(u'周三半夜2点')

    print 'required: 1 1 1 1'
    ranker = TimeRanker(u'24小时开放')
    print ranker.rank_against(u'工作日早上九点')
    print ranker.rank_against(u'节假日早上9点')
    print ranker.rank_against(u'节假日二十一点')
    print ranker.rank_against(u'周三半夜2点')

    print 'required: 1 0 1 0'
    ranker = TimeRanker(u'周一至周五 - - :9:00-21:00 - 周末 - - :10:00-23:00')
    print ranker.rank_against(u'工作日早上九点')
    print ranker.rank_against(u'节假日早上9点')
    print ranker.rank_against(u'节假日二十二点')
    print ranker.rank_against(u'周三半夜2点')

    print 'required: 0 1 0 1 0'
    ranker = TimeRanker(u'上午 - - :9:00-14:00 - 下午 - - :17:00-21:00')
    print ranker.rank_against(u'工作日早上八点')
    print ranker.rank_against(u'节假日早上9点')
    print ranker.rank_against(u'节假日二十二点')
    print ranker.rank_against(u'节假日二十一点')
    print ranker.rank_against(u'周三半夜2点')
