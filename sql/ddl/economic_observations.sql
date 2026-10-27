-- Reference schema; the Python pipeline creates this table automatically.
CREATE TABLE economic_observations (
    country_code VARCHAR NOT NULL,
    country_name VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    indicator_code VARCHAR NOT NULL,
    indicator_name VARCHAR NOT NULL,
    value DOUBLE NOT NULL,
    unit VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    retrieved_at TIMESTAMP NOT NULL,
    PRIMARY KEY (country_code, indicator_code, year)
);
