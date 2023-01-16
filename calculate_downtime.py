from datetime import datetime
date_format = "%Y-%b-%d %H:%M"
filename = "service_logs.txt"
service_id = "IC-99999"

planned_work = {"service_id":"IC-99999", "start": "2019-Apr-09 07:28", "end": "2019-Apr-09 07:28"}

end_time = datetime.strftime(datetime.now(), date_format)
end_time = datetime.strptime(str(end_time), date_format)

downtime_intervals = [] 
with open(filename) as f:
    stored_event = None
    for line in f: 
        service, status, date = line.strip().split(",")
        if service == service_id and status == 'down':
            down_date = datetime.strptime(str(date), date_format)
            duration = end_time - down_date
            stored_event = duration
        elif service == service_id and status == 'up':
            up_date = datetime.strptime(str(date), date_format)
            duration = up_date - down_date
            downtime_intervals.append(int(duration.total_seconds()))
            stored_event = None
    if stored_event:
        downtime_intervals.append(int(stored_event.total_seconds()))
print(downtime_intervals)
print(f"Total outages for service_id {service_id}: {len(downtime_intervals)}")
print(f"Total duration of outages for service_id {service_id}: {sum(downtime_intervals)}(s)")


def check_outage_planned(planned_work, outage):
    p1, p2 = planned_work
    d1, d2 = outage
    p1 = datetime.strptime(p1, date_format)
    p2 = datetime.strptime(p2, date_format)
    d1 = datetime.strptime(d1, date_format)
    d2 = datetime.strptime(d2, date_format)

    return p1<=d1<=p2 and p1<=d2<=p2

