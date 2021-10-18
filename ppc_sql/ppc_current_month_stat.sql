SET DATEFIRST 1;

with

unique_calls as (
	select 
		general_dates.simple_date,
		max(general_dates.hour) as max_hour,
		count(distinct calltouch_calls.client_phone) as unique_calls
	from calltouch_calls_facts
	left join general_traffic
		on calltouch_calls_facts.traffic_id = general_traffic.id
	left join general_dates
		on calltouch_calls_facts.dates_id = general_dates.id
	left join calltouch_calls 
		on calltouch_calls_facts.calls_id = calltouch_calls.id
	where general_dates.simple_date BETWEEN DATEADD(month, DATEDIFF(month, 0, dateadd(day, 0, convert(date, GETDATE()))), 0)
			and dateadd(day, 0, convert(date, GETDATE()))
		and concat(general_traffic.source, ' / ', general_traffic.medium) in ('yandex_tm / cpc', 'google_tm / cpc')
		and calltouch_calls_facts.account_id = 34932
	group by 
		general_dates.simple_date
),

target_calls as (
	select 
		general_dates.simple_date,
		count(distinct calltouch_calls.client_phone) as target_calls
	from calltouch_calls_facts
	left join general_traffic
		on calltouch_calls_facts.traffic_id = general_traffic.id
	left join general_dates
		on calltouch_calls_facts.dates_id = general_dates.id
	left join calltouch_calls 
		on calltouch_calls_facts.calls_id = calltouch_calls.id
	left join calltouch_calls_tags
		on calltouch_calls_facts.calls_id = calltouch_calls_tags.calls_id
	where general_dates.simple_date BETWEEN DATEADD(month, DATEDIFF(month, 0, dateadd(day, 0, convert(date, GETDATE()))), 0)
			and dateadd(day, 0, convert(date, GETDATE()))
		and concat(general_traffic.source, ' / ', general_traffic.medium) in ('yandex_tm / cpc', 'google_tm / cpc')
		and lower(calltouch_calls_tags.name) in ('{tags}')
		and calltouch_calls_facts.account_id = 34932
	group by 
		general_dates.simple_date
),

adcosts as (
	SELECT
		general_dates.simple_date,
		round(sum(distinct direct_campaigns_facts.cost) / 0.9, 2) as yd,
		sum(distinct adwords_campaigns_facts.cost * 1.2) as ga
	FROM general_dates
	left join direct_campaigns_facts
		on general_dates.id = direct_campaigns_facts.dates_id
	left join adwords_campaigns_facts
		on general_dates.id = adwords_campaigns_facts.dates_id
	where general_dates.simple_date BETWEEN DATEADD(month, DATEDIFF(month, 0, dateadd(day, 0, convert(date, GETDATE()))), 0)
			and dateadd(day, 0, convert(date, GETDATE()))
		and direct_campaigns_facts.account_id = 35271
	or general_dates.simple_date BETWEEN DATEADD(month, DATEDIFF(month, 0, dateadd(day, 0, convert(date, GETDATE()))), 0)
			and dateadd(day, 0, convert(date, GETDATE()))
		and adwords_campaigns_facts.account_id = 35946
	group by
		general_dates.simple_date
),

join_table as (
	SELECT 
		unique_calls.simple_date,
		unique_calls.max_hour,
		unique_calls.unique_calls,
		target_calls.target_calls,
		adcosts.yd,
		adcosts.ga
			
	FROM unique_calls
	left join target_calls
		on unique_calls.simple_date = target_calls.simple_date
	left join adcosts
		on unique_calls.simple_date = adcosts.simple_date
)

select 
	max(simple_date) as simple_date,
	IIF(sum(unique_calls) is null, 0, sum(unique_calls)) as total_unique_calls,
	IIF(sum(target_calls) is null, 0, sum(target_calls)) as total_target_calls,
	IIF(sum(yd) is null, 0, sum(yd)) + IIF(sum(ga) is null, 0, sum(ga)) as total_adcost,
	max(max_hour) as max_hour
from join_table


