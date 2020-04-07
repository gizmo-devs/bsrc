SET SCHEMA 'dev';
SELECT * from dev.user;
SELECT setval('user_id_seq', (SELECT MAX(id) FROM dev.user));

--CREATE TABLE rounds (
--  id INTEGER PRIMARY KEY AUTOINCREMENT,
--  comp_id INTEGER NOT NULL,
--  num INTEGER NOT NULL,
--  due_due DATE NULL
--);

--ALTER TABLE teamMembers ADD submitted_avg DECIMAL;

--=============


