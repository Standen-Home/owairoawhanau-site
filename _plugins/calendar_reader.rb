require "cgi"
require "date"
require "jekyll"
require "net/http"
require "time"
require "tzinfo"
require "uri"

module Jekyll
  class CalendarEventsGenerator < Generator
    safe false
    priority :highest

    def generate(site)
      calendar_config = site.config.fetch("google_calendar", {})
      calendar_url = calendar_config["ics_url"] || build_google_ics_url(calendar_config["id"])

      unless calendar_url
        Jekyll.logger.warn("Calendar Reader:", "No Google Calendar ICS URL or calendar id configured.")
        return
      end

      months_ahead = integer_config(calendar_config["months_ahead"], 12)
      max_events = integer_config(calendar_config["max_events"], 100)
      window_start = Time.now.utc
      window_end = window_start + (months_ahead * 31 * 24 * 60 * 60)

      generator = CalendarFeed.new(calendar_url, window_start: window_start, window_end: window_end, max_events: max_events)
      events = apply_overrides(generator.events, site.data["calendar_event_overrides"])
      Jekyll.logger.info("Calendar Reader:", "Loaded #{events.size} event(s) from #{calendar_url}")
      Jekyll.logger.warn("Calendar Reader:", "No upcoming events were found in the configured window.") if events.empty?
      site.data["calendar_events"] = events
    rescue StandardError => e
      Jekyll.logger.error("Calendar Reader:", "Error reading calendar: #{e.message}")
      raise e
    end

    private

    def build_google_ics_url(calendar_id)
      return nil if calendar_id.to_s.strip.empty?

      encoded_id = CGI.escape(calendar_id)
      "https://calendar.google.com/calendar/ical/#{encoded_id}/public/full.ics"
    end

    def integer_config(value, default)
      Integer(value || default)
    rescue ArgumentError, TypeError
      default
    end

    def apply_overrides(events, overrides)
      override_list = Array(overrides).compact
      return events if override_list.empty?

      events.map do |event|
        matched_override = override_list.find { |override| override_matches?(event, override) }
        matched_override ? merge_override(event, matched_override) : event
      end
    end

    def override_matches?(event, override)
      return false unless override.is_a?(Hash)

      uid_match = override["uid"].to_s.strip
      summary_match = override["summary"].to_s.strip
      start_match = override["start"].to_s.strip

      return event["uid"].to_s == uid_match unless uid_match.empty?

      summary_ok = summary_match.empty? || event["summary"].to_s == summary_match
      start_ok = start_match.empty? || event["start"].to_s == start_match

      summary_ok && start_ok
    end

    def merge_override(event, override)
      merged = event.dup

      %w[image image_alt teaser button_text button_url display_time].each do |key|
        value = override[key]
        merged[key] = value unless blank?(value)
      end

      merged
    end

    def blank?(value)
      value.to_s.strip.empty?
    end
  end

  class CalendarFeed
    WEEKDAY_CODES = %w[SU MO TU WE TH FR SA].freeze
    WEEKDAY_INDEX = {
      "SU" => 0,
      "MO" => 1,
      "TU" => 2,
      "WE" => 3,
      "TH" => 4,
      "FR" => 5,
      "SA" => 6
    }.freeze

    def initialize(url, window_start:, window_end:, max_events:)
      @url = url
      @window_start = window_start
      @window_end = window_end
      @max_events = max_events
    end

    def events
      masters, overrides = parse_calendar(fetch_calendar)
      expanded = masters.flat_map { |event| expand_event(event, overrides[event[:uid]] || {}) }
      expanded
        .sort_by { |event| sort_key(event[:dtstart]) }
        .first(@max_events)
        .map { |event| serialize_event(event) }
    end

    private

    def fetch_calendar(limit = 5)
      raise "Too many redirects fetching calendar." if limit <= 0

      uri = URI(@url)
      response = Net::HTTP.start(uri.host, uri.port, use_ssl: uri.scheme == "https") do |http|
        request = Net::HTTP::Get.new(uri)
        request["User-Agent"] = "OwairoaWhanauCalendar/1.0"
        http.request(request)
      end

      case response
      when Net::HTTPSuccess
        response.body.to_s.force_encoding("UTF-8").encode("UTF-8", invalid: :replace, undef: :replace)
      when Net::HTTPRedirection
        @url = URI.join(@url, response["location"]).to_s
        fetch_calendar(limit - 1)
      else
        raise "Calendar request failed with #{response.code} #{response.message}"
      end
    end

    def parse_calendar(text)
      events = []
      current = nil

      unfold_lines(text).each do |line|
        case line
        when "BEGIN:VEVENT"
          current = blank_event
        when "END:VEVENT"
          events << finalize_event(current) if current
          current = nil
        else
          next unless current

          name, params, value = parse_property(line)
          consume_property(current, name, params, value) if name
        end
      end

      masters = []
      overrides = Hash.new { |hash, key| hash[key] = {} }

      events.each do |event|
        if event[:recurrence_id]
          overrides[event[:uid]][canonical_key(event[:recurrence_id])] = event
        else
          masters << event
        end
      end

      [masters, overrides]
    end

    def blank_event
      {
        uid: nil,
        summary: nil,
        description: nil,
        location: nil,
        url: nil,
        status: nil,
        timezone: nil,
        dtstart: nil,
        dtend: nil,
        recurrence_id: nil,
        rrule: nil,
        rdate: [],
        exdate: []
      }
    end

    def finalize_event(event)
      event[:summary] = "Untitled event" if event[:summary].to_s.strip.empty?
      event
    end

    def unfold_lines(text)
      lines = []
      text.to_s.split(/\r?\n/).each do |line|
        if !lines.empty? && (line.start_with?(" ") || line.start_with?("\t"))
          lines[-1] << line[1..]
        else
          lines << line
        end
      end
      lines
    end

    def parse_property(line)
      return [nil, {}, nil] unless line.include?(":")

      name_and_params, value = line.split(":", 2)
      parts = name_and_params.split(";")
      name = parts.shift
      params = parts.each_with_object({}) do |part, memo|
        key, param_value = part.split("=", 2)
        memo[key] = param_value
      end

      [name, params, value]
    end

    def consume_property(event, name, params, value)
      case name
      when "UID"
        event[:uid] = normalize_text(value)
      when "SUMMARY"
        event[:summary] = normalize_text(value)
      when "DESCRIPTION"
        event[:description] = normalize_text(value)
      when "LOCATION"
        event[:location] = normalize_text(value)
      when "URL"
        event[:url] = normalize_text(value)
      when "STATUS"
        event[:status] = normalize_text(value)
      when "DTSTART"
        event[:timezone] ||= params["TZID"]
        event[:dtstart] = parse_datetime(value, params)
      when "DTEND"
        event[:dtend] = parse_datetime(value, params)
      when "RECURRENCE-ID"
        event[:recurrence_id] = parse_datetime(value, params)
      when "RRULE"
        event[:rrule] = parse_rrule(value, params)
      when "RDATE"
        event[:rdate].concat(parse_multi_datetime(value, params))
      when "EXDATE"
        event[:exdate].concat(parse_multi_datetime(value, params))
      end
    end

    def parse_rrule(value, _params)
      value.to_s.split(";").each_with_object({}) do |part, memo|
        key, rule_value = part.split("=", 2)
        memo[key] = rule_value
      end
    end

    def parse_multi_datetime(value, params)
      value.to_s.split(",").filter_map { |part| parse_datetime(part, params) }
    end

    def parse_datetime(value, params)
      value = value.to_s.strip
      return nil if value.empty?

      return Date.strptime(value, "%Y%m%d") if params["VALUE"] == "DATE" || value.match?(/\A\d{8}\z/)

      tzid = params["TZID"]
      if value.end_with?("Z")
        return Time.strptime(value, "%Y%m%dT%H%M%SZ").utc
      end

      format = value.length == 13 ? "%Y%m%dT%H%M" : "%Y%m%dT%H%M%S"
      time = Time.strptime(value, format)
      return time unless tzid

      timezone = TZInfo::Timezone.get(tzid)
      timezone.local_time(time.year, time.month, time.day, time.hour, time.min, time.sec).to_time
    rescue TZInfo::InvalidTimezoneIdentifier, TZInfo::PeriodNotFound, TZInfo::AmbiguousTime
      Time.parse(value)
    rescue ArgumentError
      nil
    end

    def normalize_text(value)
      value.to_s
        .force_encoding("UTF-8")
        .encode("UTF-8", invalid: :replace, undef: :replace)
        .gsub("\\n", "\n")
        .gsub("\\,", ",")
        .gsub("\\;", ";")
        .gsub("\\\\", "\\")
        .strip
    end

    def expand_event(event, overrides)
      return [] if cancelled?(event) || event[:dtstart].nil?

      duration = event_duration(event)
      exdates = event[:exdate].map { |value| canonical_key(value) }.to_h { |key| [key, true] }
      results = []
      seen = {}

      starts = if event[:rrule]
        expand_rule(event)
      else
        [event[:dtstart]]
      end

      starts.concat(event[:rdate])
      starts.sort_by! { |value| sort_key(value) }

      starts.each do |start_value|
        original_key = canonical_key(start_value)
        next if seen[original_key]
        next if exdates[original_key]

        seen[original_key] = true
        occurrence = overrides[original_key] || occurrence_from_master(event, start_value, duration)
        next if cancelled?(occurrence)
        next unless within_window?(occurrence[:dtstart], occurrence[:dtend] || calculate_end(occurrence[:dtstart], duration))

        results << occurrence
      end

      results
    end

    def expand_rule(event)
      rule = event[:rrule] || {}
      frequency = rule.fetch("FREQ", "").upcase
      return [event[:dtstart]] if frequency.empty?

      case frequency
      when "DAILY"
        expand_daily(event, rule)
      when "WEEKLY"
        expand_weekly(event, rule)
      when "MONTHLY"
        expand_monthly(event, rule)
      when "YEARLY"
        expand_yearly(event, rule)
      else
        [event[:dtstart]]
      end
    end

    def expand_daily(event, rule)
      interval = positive_integer(rule["INTERVAL"], 1)
      limit = recurrence_limit(event, rule)
      current = event[:dtstart]
      occurrences = []
      generated = 0

      while current && current <= limit[:until] && generated < limit[:count]
        if matches_daily_filters?(current, event, rule)
          occurrences << current
          generated += 1
        end
        current = shift_days(current, interval, event[:timezone], event[:dtstart])
      end

      occurrences
    end

    def expand_weekly(event, rule)
      interval = positive_integer(rule["INTERVAL"], 1)
      limit = recurrence_limit(event, rule)
      start_value = event[:dtstart]
      week_days = parse_byday(rule["BYDAY"])
      week_days = [weekday_code(start_value)] if week_days.empty?
      week_days = week_days.map { |entry| entry[:day] }

      week_start = date_value(start_value) - date_value(start_value).wday
      occurrences = []
      generated = 0

      while generated < limit[:count]
        week_days.each do |day_code|
          day_index = WEEKDAY_INDEX.fetch(day_code)
          candidate_date = week_start + day_index
          candidate = combine_date_and_time(candidate_date, start_value, event[:timezone])
          next if candidate < start_value
          break if candidate > limit[:until]

          occurrences << candidate
          generated += 1
          break if generated >= limit[:count]
        end

        break if combine_date_and_time(week_start + 7 * interval, start_value, event[:timezone]) > limit[:until]

        week_start += 7 * interval
      end

      occurrences.sort_by { |value| sort_key(value) }
    end

    def expand_monthly(event, rule)
      interval = positive_integer(rule["INTERVAL"], 1)
      limit = recurrence_limit(event, rule)
      start_value = event[:dtstart]
      occurrences = []
      generated = 0
      cursor = date_value(start_value)

      while generated < limit[:count]
        candidates = monthly_candidates(cursor, start_value, event[:timezone], rule)
        candidates.sort_by! { |value| sort_key(value) }

        candidates.each do |candidate|
          next if candidate < start_value
          break if candidate > limit[:until]

          occurrences << candidate
          generated += 1
          break if generated >= limit[:count]
        end

        cursor = shift_month(cursor, interval)
        break if combine_date_and_time(cursor, start_value, event[:timezone]) > limit[:until]
      end

      occurrences
    end

    def expand_yearly(event, rule)
      interval = positive_integer(rule["INTERVAL"], 1)
      limit = recurrence_limit(event, rule)
      start_value = event[:dtstart]
      occurrences = []
      generated = 0
      year = date_value(start_value).year

      while generated < limit[:count]
        candidates = yearly_candidates(year, start_value, event[:timezone], rule)
        candidates.sort_by! { |value| sort_key(value) }

        candidates.each do |candidate|
          next if candidate < start_value
          break if candidate > limit[:until]

          occurrences << candidate
          generated += 1
          break if generated >= limit[:count]
        end

        year += interval
        break if combine_date_and_time(Date.new(year, start_value.month, start_value.day), start_value, event[:timezone]) > limit[:until]
      end

      occurrences
    end

    def matches_daily_filters?(candidate, event, rule)
      byday = parse_byday(rule["BYDAY"]).map { |entry| entry[:day] }
      return true if byday.empty?

      byday.include?(weekday_code(candidate)) || weekday_code(candidate) == weekday_code(event[:dtstart])
    end

    def monthly_candidates(cursor_date, start_value, timezone_id, rule)
      bymonthdays = parse_integer_list(rule["BYMONTHDAY"])
      byday = parse_byday(rule["BYDAY"])
      bysetpos = parse_integer_list(rule["BYSETPOS"])

      if !bysetpos.empty? && !byday.empty?
        if byday.any? { |entry| entry[:position] }
          weekday_candidates = byday.filter_map do |entry|
            next unless entry[:position]

            nth_weekday_of_month(cursor_date.year, cursor_date.month, entry[:day], entry[:position], start_value, timezone_id)
          end
          return weekday_candidates
        end

        all_candidates = byday.flat_map do |entry|
          all_weekdays_of_month(cursor_date.year, cursor_date.month, entry[:day], start_value, timezone_id)
        end
        all_candidates.sort_by! { |value| sort_key(value) }
        return bysetpos.filter_map { |position| occurrence_at_position(all_candidates, position) }
      end

      unless bymonthdays.empty?
        return bymonthdays.filter_map do |day|
          build_monthday(cursor_date.year, cursor_date.month, day, start_value, timezone_id)
        end
      end

      unless byday.empty?
        return byday.flat_map do |entry|
          if entry[:position]
            [nth_weekday_of_month(cursor_date.year, cursor_date.month, entry[:day], entry[:position], start_value, timezone_id)].compact
          else
            all_weekdays_of_month(cursor_date.year, cursor_date.month, entry[:day], start_value, timezone_id)
          end
        end
      end

      [build_monthday(cursor_date.year, cursor_date.month, date_value(start_value).day, start_value, timezone_id)].compact
    end

    def yearly_candidates(year, start_value, timezone_id, rule)
      months = parse_integer_list(rule["BYMONTH"])
      months = [date_value(start_value).month] if months.empty?
      monthdays = parse_integer_list(rule["BYMONTHDAY"])
      monthdays = [date_value(start_value).day] if monthdays.empty?

      months.flat_map do |month|
        monthdays.filter_map do |day|
          build_monthday(year, month, day, start_value, timezone_id)
        end
      end
    end

    def recurrence_limit(event, rule)
      until_value = parse_datetime(rule["UNTIL"], {}) || @window_end
      until_value = coerce_limit_type(until_value, event[:dtstart])
      window_limit = coerce_limit_type(@window_end, event[:dtstart])
      until_value = window_limit if until_value > window_limit
      count_value = positive_integer(rule["COUNT"], 10_000)
      { until: until_value, count: count_value }
    end

    def occurrence_from_master(event, start_value, duration)
      occurrence = event.dup
      occurrence[:dtstart] = start_value
      occurrence[:dtend] = calculate_end(start_value, duration)
      occurrence
    end

    def calculate_end(start_value, duration)
      return nil unless duration

      if start_value.is_a?(Date) && !start_value.is_a?(Time)
        start_value + duration
      else
        start_value + duration
      end
    end

    def event_duration(event)
      return nil unless event[:dtend]

      event[:dtend] - event[:dtstart]
    end

    def within_window?(start_value, end_value)
      normalized_start = time_or_date(start_value)
      normalized_end = time_or_date(end_value || start_value)
      normalized_end >= @window_start && normalized_start <= @window_end
    end

    def time_or_date(value)
      return Time.utc(value.year, value.month, value.day) if value.is_a?(Date) && !value.is_a?(Time)

      value.getutc
    end

    def cancelled?(event)
      event[:status].to_s.upcase == "CANCELLED"
    end

    def serialize_event(event)
      output = {
        "uid" => event[:uid],
        "summary" => event[:summary],
        "start" => format_datetime(event[:dtstart]),
        "all_day" => all_day_event?(event[:dtstart], event[:dtend]),
        "display_time" => format_display_time(event[:dtstart], event[:dtend])
      }

      output["end"] = format_datetime(event[:dtend]) if event[:dtend]
      output["location"] = event[:location] unless blank?(event[:location])
      output["description"] = event[:description] unless blank?(event[:description])
      output["url"] = event[:url] unless blank?(event[:url])
      output
    end

    def all_day_event?(start_value, end_value)
      start_is_date = start_value.is_a?(Date) && !start_value.is_a?(Time)
      end_is_date = end_value.nil? || (end_value.is_a?(Date) && !end_value.is_a?(Time))
      start_is_date && end_is_date
    end

    def format_display_time(start_value, end_value)
      return "" unless start_value

      if all_day_event?(start_value, end_value)
        return start_value.strftime("%a %d %b %Y") if start_value.respond_to?(:strftime)

        return start_value.to_s
      end

      return start_value.strftime("%-l:%M %p, %a %d %b %Y") unless end_value

      same_day = date_value(start_value) == date_value(end_value)

      if same_day
        "#{start_value.strftime('%-l:%M %p')} - #{end_value.strftime('%-l:%M %p')}, #{start_value.strftime('%a %d %b %Y')}"
      else
        "#{start_value.strftime('%-l:%M %p, %a %d %b %Y')} - #{end_value.strftime('%-l:%M %p, %a %d %b %Y')}"
      end
    end

    def format_datetime(value)
      return value.iso8601 if value.is_a?(Time)
      return value.iso8601 if value.is_a?(DateTime)
      return value.iso8601 if value.is_a?(Date)

      value.to_s
    end

    def canonical_key(value)
      format_datetime(value)
    end

    def sort_key(value)
      return value.to_time.utc.to_i if value.is_a?(DateTime)
      return value.getutc.to_i if value.is_a?(Time)
      return Time.utc(value.year, value.month, value.day).to_i if value.is_a?(Date)

      0
    end

    def parse_byday(value)
      value.to_s.split(",").filter_map do |entry|
        next if entry.empty?

        match = entry.match(/\A([+-]?\d+)?([A-Z]{2})\z/)
        next unless match

        {
          position: match[1]&.to_i,
          day: match[2]
        }
      end
    end

    def parse_integer_list(value)
      value.to_s.split(",").filter_map do |entry|
        Integer(entry)
      rescue ArgumentError, TypeError
        nil
      end
    end

    def positive_integer(value, default)
      integer = Integer(value || default)
      integer.positive? ? integer : default
    rescue ArgumentError, TypeError
      default
    end

    def weekday_code(value)
      WEEKDAY_CODES[date_value(value).wday]
    end

    def date_value(value)
      value.is_a?(Date) && !value.is_a?(Time) ? value : value.to_date
    end

    def combine_date_and_time(date, reference, timezone_id = nil)
      return date if reference.is_a?(Date) && !reference.is_a?(Time)

      if timezone_id
        timezone = TZInfo::Timezone.get(timezone_id)
        return timezone.local_time(date.year, date.month, date.day, reference.hour, reference.min, reference.sec).to_time
      end

      Time.new(date.year, date.month, date.day, reference.hour, reference.min, reference.sec, reference.utc_offset)
    end

    def shift_days(value, count, timezone_id = nil, reference = value)
      return value + count if value.is_a?(Date) && !value.is_a?(Time)

      combine_date_and_time(date_value(value) + count, reference, timezone_id)
    end

    def shift_month(date, count)
      year = date.year
      month = date.month + count

      while month > 12
        month -= 12
        year += 1
      end

      while month < 1
        month += 12
        year -= 1
      end

      day = [date.day, days_in_month(year, month)].min
      Date.new(year, month, day)
    end

    def build_monthday(year, month, day, reference, timezone_id = nil)
      target_day = if day.negative?
        days_in_month(year, month) + day + 1
      else
        day
      end

      return nil if target_day < 1 || target_day > days_in_month(year, month)

      combine_date_and_time(Date.new(year, month, target_day), reference, timezone_id)
    end

    def nth_weekday_of_month(year, month, day_code, position, reference, timezone_id = nil)
      weekday = WEEKDAY_INDEX.fetch(day_code)
      days = (1..days_in_month(year, month)).filter do |day|
        Date.new(year, month, day).wday == weekday
      end

      day = if position.negative?
        days[position]
      else
        days[position - 1]
      end

      return nil unless day

      combine_date_and_time(Date.new(year, month, day), reference, timezone_id)
    end

    def all_weekdays_of_month(year, month, day_code, reference, timezone_id = nil)
      weekday = WEEKDAY_INDEX.fetch(day_code)
      (1..days_in_month(year, month)).filter_map do |day|
        date = Date.new(year, month, day)
        next unless date.wday == weekday

        combine_date_and_time(date, reference, timezone_id)
      end
    end

    def occurrence_at_position(candidates, position)
      return nil if position.zero?

      position.negative? ? candidates[position] : candidates[position - 1]
    end

    def coerce_limit_type(value, reference)
      return value.to_date if reference.is_a?(Date) && !reference.is_a?(Time) && value.respond_to?(:to_date)
      return Time.utc(value.year, value.month, value.day, 23, 59, 59) if reference.is_a?(Time) && value.is_a?(Date) && !value.is_a?(Time)

      value
    end

    def days_in_month(year, month)
      Date.new(year, month, -1).day
    end

    def blank?(value)
      value.to_s.strip.empty?
    end
  end
end
