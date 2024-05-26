DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS urls_checks;

CREATE TABLE urls(
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) NOT NULL UNIQUE,
    created_at timestamp NOT NULL
    );

CREATE TABLE urls_checks(
id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
url_id bigint REFERENCES urls (id),
response_code int,
h1 varchar(255),
title varchar(255),
description varchar(255),
created_at date NOT NULL
);
