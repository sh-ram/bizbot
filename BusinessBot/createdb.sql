CREATE TABLE IF NOT EXISTS currency_index (
    id_currency_index nchar NOT NULL PRIMARY KEY,
    name nchar NOT NULL UNIQUE,
    currency_unit integer NOT NULL,
    symbol nchar(50) NULL DEFAULT NULL,
    country nchar NULL UNIQUE DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS index_link (
    id_index_link nchar NOT NULL PRIMARY KEY,
    currency_index_id nchar NOT NULL,
    language nchar(2) NULL DEFAULT NULL,       

    FOREIGN KEY (currency_index_id) REFERENCES currency_index(id_currency_index)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS burse (
    url nchar(100) NOT NULL PRIMARY KEY,
    name nchar NULL,
    template nchar(150) NULL UNIQUE DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS index_selector (
    id_index_selector nchar(150) NULL PRIMARY KEY,
    currency_index_id nchar NOT NULL,
    url nchar NOT NULL,

    FOREIGN KEY (currency_index_id) REFERENCES currency_index(id_currency_index)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
    FOREIGN KEY (url) REFERENCES burse(url)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS job(
    -- id_job integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    currency_index_id nchar(3) NOT NULL,
    user_id integer NOT NULL,
    chat_id integer NOT NULL,
    status char(7) CHECK (status IN ('active', 'disable'))
        DEFAULT 'active',
    execute_time time NOT NULL,
    days char(7) NOT NULL DEFAULT '0123456',
    last_change_datetime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (currency_index_id) REFERENCES currency_index(id_currency_index)
        ON UPDATE CASCADE
        ON DELETE RESTRICT   
);

CREATE TABLE IF NOT EXISTS job_log(
  id_job_log integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  currency_index_id nchar(3) NULL DEFAULT NULL,
  user_id_ integer NULL DEFAULT NULL,
  chat_id_ integer NULL DEFAULT NULL,
  status_ char(7) NULL CHECK (status_ IN ('active', 'disable'))
        DEFAULT NULL,
  execute_time_ time NULL DEFAULT NULL,
  days_ chat(7) NULL DEFAULT NULL,
  last_change_datetime_ datetime NULL DEFAULT NULL,
  change_datetime datetime NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX currencyIndexId_url
ON index_selector (currency_index_id, url);

CREATE UNIQUE INDEX currency_chatId 
ON job (currency_index_id, chat_id);

CREATE INDEX userId_chatId_executeTime
ON job_log (chat_id_, execute_time_);

CREATE TRIGGER insert_index_selector AFTER INSERT ON `burse`
    FOR EACH ROW
    -- Insert template values to index_selector table
    -- if burse insert query literally contain '{currency}' in `template`
    BEGIN
        INSERT INTO index_selector 
            (id_index_selector, currency_index_id, url) 
        SELECT 
            CASE WHEN INSTR(template, '{currency}') > 0 THEN
            REPLACE(template, '{currency}', LOWER(id_currency_index)) END selector,   
            id_currency_index currency, url
        FROM currency_index, (SELECT NEW.template template, NEW.url url);
    END
;

CREATE TRIGGER update_job_status 
    BEFORE UPDATE OF `execute_time`, `user_id`, `status`,
                     `days`
    ON `job`
        -- Change status to 'active' with minor upset row only.
    FOR EACH ROW
        BEGIN
            UPDATE job SET status = 'active', last_change_datetime = CURRENT_TIMESTAMP
            WHERE `currency_index_id` = NEW.`currency_index_id`
            AND NEW.`chat_id` = `chat_id`;  
            
            INSERT INTO `job_log` 
                    (currency_index_id, user_id_, chat_id_, status_,
                    execute_time_, days_, last_change_datetime_) 
            VALUES (NEW.currency_index_id, NEW.user_id, 
                    NEW.chat_id, NEW.status, 
                    NEW.execute_time, NEW.days,
                    NEW.last_change_datetime);
        END
;

CREATE TRIGGER insert_job_log AFTER INSERT ON `job`
    FOR EACH ROW
    -- Log insert values.
    BEGIN
        INSERT INTO `job_log` (currency_index_id, user_id_, chat_id_, status_,
                                execute_time_, days_, last_change_datetime_) 
        VALUES (NEW.`currency_index_id`, NEW.`user_id`,
                NEW.`chat_id`, NEW.`status`,  
                NEW.`execute_time`, NEW.`days`,
                NEW.`last_change_datetime`);
    END
;

INSERT INTO currency_index (name, id_currency_index, currency_unit, symbol, country) VALUES
    ('Доллар',      'USD',  1, '&#36;', 'США'),
    ('Евро',        'EUR',  1, '&#8364;', NULL),
    ('Китайский юань',      'CNY',  1, NULL, 'Китай'),
    ('Фунт стерлингов',     'GBP',  1, NULL, 'Великобритания'),
    ('Казахстанский тенге', 'KZT',  100, NULL, 'Казахстанский тенге'),
    ('Швейцарский франк',   'CHF',  1, NULL, NULL),
    ('Белорусский рубль',   'BYN',  1, NULL, NULL),
    ('Украинская гривна',   'UAH',  10, NULL, NULL),
    ('Японская йена',       'JPY',  100, NULL, NULL),
    ('Турецкая лира',       'TRY',  1, NULL, NULL),
    ('Польский злотый',     'PLN',  1, NULL, NULL),
    ('Канадский доллар',    'CAD',  1, NULL, NULL),
    ('Чешская крона',       'CZK',  10, NULL, NULL),
    ('Узбекский сум',       'UZS',  10000, NULL, NULL),
    ('Шведская крона',      'SEK',  10, NULL, NULL),
    ('Норвежская крона',    'NOK',  10, NULL, NULL),
    ('Болгарский лев',      'BGN',  1, NULL, NULL),
    ('Армянский драм',      'AMD',  100, NULL, NULL),
    ('Индийская рупия',     'INR',  100, NULL, NULL),
    ('Южнокорейская вона',  'KRW',  1000, NULL, NULL),
    ('Киргизский сом',      'KGS',  100, NULL, NULL),
    ('Венгерский форинт',   'HUF',  100, NULL, NULL),
    ('Гонконгский доллар',  'HKD',  10, NULL, NULL),
    ('Туркменский манат',   'TMT',  1, NULL, NULL),
    ('Датская крона',       'DKK',  10, NULL, NULL),
    ('Австралийский доллар',        'AUD',  1, NULL, NULL),
    ('Азербайджанский манат',       'AZN',  1, NULL, NULL),
    ('Бразильский реал',    'BRL',  1, NULL, NULL),
    ('Сингапурский доллар', 'SGD',  1, NULL, NULL),
    ('Румынский лей',       'RON',  1, NULL, NULL),
    ('Таджикский сомони',   'TJS',  10, NULL, NULL),
    ('СДР', 'XDR',  1, NULL, NULL),
    ('Молдавский лей',      'MDL',  10, NULL, NULL)
;

UPDATE currency_index SET symbol="&#36;", country="США"  WHERE id_currency_index="USD";
UPDATE currency_index SET symbol="&#8364;" WHERE id_currency_index="EUR";
UPDATE currency_index SET country="Великобритания" WHERE id_currency_index="GBP";
UPDATE currency_index SET country="Казахстанский тенге" WHERE id_currency_index="KZT";

INSERT INTO burse(name, url, template) VALUES
    ('Mainfin', 'https://mainfin.ru/currency/cb-rf', '#cbrf_today_{currency}')
;

INSERT INTO index_link (id_index_link, currency_index_id, language) VALUES
    ('Dollar',      'USD', 'en'),
    ('Euro',        'EUR', 'en'),
    ('Chinese yuan',        'CNY', 'en'),
    ('Pound',       'GBP', 'en'),
    ('Kazakhstani tenge',   'KZT', 'en'),
    ('Swiss franc', 'CHF', 'en'),
    ('Belarusian ruble',    'BYN', 'en'),
    ('Ukrainian hryvnia',   'UAH', 'en'),
    ('Japanese yen',        'JPY', 'en'),
    ('Turkish lira',        'TRY', 'en'),
    ('Polish zloty',        'PLN', 'en'),
    ('Canadian dollar',     'CAD', 'en'),
    ('Czech koruna',        'CZK', 'en'),
    ('Czech crown', 'CZK', 'en'),
    ('Uzbek sum',   'UZS', 'en'),
    ('Swedish Krona',       'SEK', 'en'),
    ('Norwegian Krone',     'NOK', 'en'),
    ('Bulgarian Lev',       'BGN', 'en'),
    ('Armenian dram',       'AMD', 'en'),
    ('Indian rupee',        'INR', 'en'),
    ('South Korean won',    'KRW', 'en'),
    ('Kyrgyz som',  'KGS', 'en'),
    ('Hungarian forint',    'HUF', 'en'),
    ('Hong Kong dollar',    'HKD', 'en'),
    ('Turkmen manat',       'TMT', 'en'),
    ('Danish Krone',        'DKK', 'en'),
    ('Australian dollar',   'AUD', 'en'),
    ('Azerbaijani manat',   'AZN', 'en'),
    ('Brazilian real',      'BRL', 'en'),
    ('Singapore dollar',    'SGD', 'en'),
    ('Romanian LEU',        'RON', 'en'),
    ('Tajik somoni',        'TJS', 'en'),
    ('sdr', 'XDR', 'en'),
    ('special drawing right',       'XDR', 'en'),
    ('Moldovan LEU',        'MDL', 'en')
;
--     ('RON', '#cdrf_today_ron', 'Mainfin'),
--     ('TJS', '#cdrf_today_tjs', 'Mainfin'),
--     ('XDR', '#cdrf_today_xdr', 'Mainfin'),
--     ('MDL', '#cdrf_today_mdl', 'Mainfin');

