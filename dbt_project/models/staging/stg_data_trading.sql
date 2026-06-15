with source_data as (
    select * from {{ source('raw_trading', 'data_trading') }}
),

cleaned as (
    select
        trim(Name) as company_name,
        cast(Open as FLOAT64) as open_price,
        cast(High as FLOAT64) as high_price,
        cast(Low as FLOAT64) as low_price,
        cast(Close as FLOAT64) as close_price,
        cast(Volume as FLOAT64) as volume,
        cast(`Date et Heure` as TIMESTAMP) as date_et_heure
    from source_data
    where Name is not null and `Date et Heure` is not null
),

deduplicated as (
    select
        company_name,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        date_et_heure,
        row_number() over (
            partition by company_name, date_et_heure 
            order by volume desc, close_price desc
        ) as row_num
    from cleaned
)

select
    company_name,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    date_et_heure
from deduplicated
where row_num = 1
