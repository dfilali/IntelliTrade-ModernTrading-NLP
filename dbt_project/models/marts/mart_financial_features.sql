with staging_data as (
    select * from {{ ref('stg_data_trading') }}
),

ordered_features as (
    select
        company_name,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        date_et_heure,
        -- Moyennes mobiles simples sur 5 et 20 périodes
        avg(close_price) over (
            partition by company_name 
            order by date_et_heure 
            rows between 4 preceding and current row
        ) as sma_5,
        avg(close_price) over (
            partition by company_name 
            order by date_et_heure 
            rows between 19 preceding and current row
        ) as sma_20,
        -- Rendement par rapport à la période précédente
        (close_price - lag(close_price) over (
            partition by company_name 
            order by date_et_heure
        )) / nullif(lag(close_price) over (
            partition by company_name 
            order by date_et_heure
        ), 0) as daily_return,
        -- Moyenne mobile simple du volume
        avg(volume) over (
            partition by company_name 
            order by date_et_heure 
            rows between 4 preceding and current row
        ) as volume_sma_5
    from staging_data
)

select * from ordered_features
order by company_name, date_et_heure
