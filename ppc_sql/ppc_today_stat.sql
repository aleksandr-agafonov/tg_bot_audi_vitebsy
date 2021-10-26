with

unique_calls_yandex as (
	select 
		general_dates.simple_date,
		max(general_dates.hour) as max_hour,
		count(distinct calltouch_calls.client_phone) as unique_calls_yandex
	from calltouch_calls_facts
	left join general_traffic
		on calltouch_calls_facts.traffic_id = general_traffic.id
	left join general_dates
		on calltouch_calls_facts.dates_id = general_dates.id
	left join calltouch_calls 
		on calltouch_calls_facts.calls_id = calltouch_calls.id
	where general_dates.simple_date = dateadd(day, 0, convert(date, GETDATE()))
		and concat(general_traffic.source, ' / ', general_traffic.medium) = 'yandex_tm / cpc'
		and calltouch_calls_facts.account_id = 34932
	group by 
		general_dates.simple_date
),

unique_calls_google as (
	select 
		general_dates.simple_date,
		max(general_dates.hour) as max_hour,
		count(distinct calltouch_calls.client_phone) as unique_calls_google
	from calltouch_calls_facts
	left join general_traffic
		on calltouch_calls_facts.traffic_id = general_traffic.id
	left join general_dates
		on calltouch_calls_facts.dates_id = general_dates.id
	left join calltouch_calls 
		on calltouch_calls_facts.calls_id = calltouch_calls.id
	where general_dates.simple_date = dateadd(day, 0, convert(date, GETDATE()))
		and concat(general_traffic.source, ' / ', general_traffic.medium) = 'google_tm / cpc'
		and calltouch_calls_facts.account_id = 34932
	group by 
		general_dates.simple_date
),


target_calls_yandex as (
	select 
		general_dates.simple_date,
		count(distinct calltouch_calls.client_phone) as target_calls_yandex
	from calltouch_calls_facts
	left join general_traffic
		on calltouch_calls_facts.traffic_id = general_traffic.id
	left join general_dates
		on calltouch_calls_facts.dates_id = general_dates.id
	left join calltouch_calls 
		on calltouch_calls_facts.calls_id = calltouch_calls.id
	left join calltouch_calls_tags
		on calltouch_calls_facts.calls_id = calltouch_calls_tags.calls_id
	where general_dates.simple_date = dateadd(day, 0, convert(date, GETDATE()))
		and concat(general_traffic.source, ' / ', general_traffic.medium) = 'yandex_tm / cpc'
		and lower(calltouch_calls_tags.name) in ('{tags}')
		and calltouch_calls_facts.account_id = 34932
	group by 
		general_dates.simple_date
),

target_calls_google as (
	select 
		general_dates.simple_date,
		count(distinct calltouch_calls.client_phone) as target_calls_google
	from calltouch_calls_facts
	left join general_traffic
		on calltouch_calls_facts.traffic_id = general_traffic.id
	left join general_dates
		on calltouch_calls_facts.dates_id = general_dates.id
	left join calltouch_calls 
		on calltouch_calls_facts.calls_id = calltouch_calls.id
	left join calltouch_calls_tags
		on calltouch_calls_facts.calls_id = calltouch_calls_tags.calls_id
	where general_dates.simple_date = dateadd(day, 0, convert(date, GETDATE()))
		and concat(general_traffic.source, ' / ', general_traffic.medium) = 'google_tm / cpc'
		and lower(calltouch_calls_tags.name) in ('{tags}')
		and calltouch_calls_facts.account_id = 34932
	group by 
		general_dates.simple_date
),

adcosts as (
	SELECT
		general_dates.simple_date,
		round(sum(distinct direct_campaigns_facts.cost) / 0.9, 2) as yd_adcost,
		sum(distinct adwords_campaigns_facts.cost * 1.2) as ga_adcost
	FROM general_dates
	full join direct_campaigns_facts
		on general_dates.id = direct_campaigns_facts.dates_id
	full join adwords_campaigns_facts
		on general_dates.id = adwords_campaigns_facts.dates_id
	where simple_date = dateadd(day, 0, convert(date, GETDATE()))
		and direct_campaigns_facts.account_id = 35271
	or simple_date = dateadd(day, 0, convert(date, GETDATE()))
		and adwords_campaigns_facts.account_id = 35946
	group by
		general_dates.simple_date
),

join_table as (
	SELECT 
		unique_calls_yandex.simple_date,
		unique_calls_yandex.max_hour,
		unique_calls_yandex.unique_calls_yandex,
		
		target_calls_yandex.target_calls_yandex,
		
		unique_calls_google.unique_calls_google,
		
		target_calls_google.target_calls_google,
		
		adcosts.yd_adcost,
		adcosts.ga_adcost
			
	FROM unique_calls_yandex
	full join target_calls_yandex
		on unique_calls_yandex.simple_date = target_calls_yandex.simple_date
	full JOIN unique_calls_google
		on unique_calls_yandex.simple_date = unique_calls_google.simple_date
	full join target_calls_google
		on unique_calls_yandex.simple_date = target_calls_google.simple_date
	full join adcosts
		on unique_calls_yandex.simple_date = adcosts.simple_date
)

select 
	simple_date,
	IIF(sum(unique_calls_yandex) is null, 0, sum(unique_calls_yandex)) + IIF(sum(unique_calls_google) is null, 0, sum(unique_calls_google)) as total_unique_calls,
	IIF(sum(target_calls_yandex) is null, 0, sum(target_calls_yandex)) + IIF(sum(target_calls_google) is null, 0, sum(target_calls_google)) as total_target_calls,
	IIF(sum(yd_adcost) is null, 0, sum(yd_adcost)) + IIF(sum(ga_adcost) is null, 0, sum(ga_adcost)) as total_adcost,
	max_hour,
	IIF(sum(target_calls_yandex) is null, 0, sum(target_calls_yandex)) as target_calls_yandex,
	IIF(sum(target_calls_google) is null, 0, sum(target_calls_google)) as target_calls_google,
	round(IIF(sum(yd_adcost) is null, 0, sum(yd_adcost)), 0) as yd_adcost,
	round(IIF(sum(ga_adcost) is null, 0, sum(ga_adcost)), 0) as ga_adcost
	
from join_table
group by 	
	simple_date, max_hour

