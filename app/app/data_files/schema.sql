-- Clear all tables
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS teamMembers;
DROP TABLE IF EXISTS competitions;
DROP TABLE IF EXISTS compTeam;
DROP TABLE IF EXISTS scores;

-- Recreate the Tables
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  surname TEXT NOT NULL,
  username TEXT UNIQUE NOT NULL,
  --password TEXT NOT NULL
  password TEXT,
  permission_level TEXT DEFAULT "user" NOT NULL
);

--INSERT INTO user (first_name, surname, username) VALUES ('Craig', 'Attwood', 'craigattwood');
--INSERT INTO user (first_name, surname, username) VALUES ('Mike', 'Lemon', 'mlemon');
--INSERT INTO user (first_name, surname, username) VALUES ('Dave', 'Lemon', 'dlemon');
--INSERT INTO user (first_name, surname, username) VALUES ('Ian', 'Bisson', 'ibisson');
--INSERT INTO user (first_name, surname, username) VALUES ('Simon', 'Teed', 'steed');
--INSERT INTO user (first_name, surname, username) VALUES ('Jack', 'Smith', 'Jsmith');
--INSERT INTO user (first_name, surname, username) VALUES ('Matt', 'Robinson', 'mRobinson');



CREATE TABLE team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL,
    team_size INTEGER NULL,
    season TEXT NOT NULL
);

--INSERT INTO team (team_name, team_size, season) VALUES ('Budleigh A Team', 3, '2019/20');
--INSERT INTO team (team_name, team_size, season) VALUES ('Budleigh B Team', 2, '2019/20');

CREATE TABLE teamMembers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL
);

--INSERT INTO teamMembers (user_id, team_id) VALUES (1,1);
--INSERT INTO teamMembers (user_id, team_id) VALUES (2,1);
--INSERT INTO teamMembers (user_id, team_id) VALUES (3,1);
--
--INSERT INTO teamMembers (user_id, team_id) VALUES (4,2);
--INSERT INTO teamMembers (user_id, team_id) VALUES (6,2);

CREATE TABLE competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_name TEXT NOT NULL,
    season TEXT NULL,
    rounds INTEGER NULL,
    round1_due DATE NULL,
    round2_due DATE NULL,
    round3_due DATE NULL,
    round4_due DATE NULL,
    round5_due DATE NULL,
    round6_due DATE NULL,
    round7_due DATE NULL,
    round8_due DATE NULL,
    round9_due DATE NULL,
    round10_due DATE NULL,
    round11_due DATE NULL,
    round12_due DATE NULL,
    round13_due DATE NULL,
    round14_due DATE NULL,
    round15_due DATE NULL,
    round16_due DATE NULL,
    round17_due DATE NULL,
    round18_due DATE NULL
);

CREATE TABLE rounds (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comp_id INTEGER NOT NULL,
  num INTEGER NOT NULL,
  due_date DATE NULL
);

--INSERT INTO competitions (competition_name, season, rounds) VALUES ('Winter League', '2019/20', 18);
--INSERT INTO competitions (competition_name, season, rounds) VALUES ('Winter League - B', '2019/20', 18);

CREATE TABLE compTeam (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NULL,
    competition_id INTEGER NULL
);

--INSERT INTO compTeam (team_id, competition_id) VALUES(1,1);
--INSERT INTO compTeam (team_id, competition_id) VALUES(2,2);


CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    estimated INTEGER NULL,
    result INTEGER NULL,
    completed DATE NOT NULL
);


--INSERT INTO scores (competition_id, user_id, round, estimated, result, completed) VALUES (1, 1, 1, 100, 100, '2019-09-01');
--INSERT INTO scores (competition_id, user_id, round, estimated, result, completed) VALUES (1, 1, 2, 99, 100, '2019-09-07');
--INSERT INTO scores (competition_id, user_id, round, estimated, result, completed) VALUES (1, 1, 3, 99, 98, '2019-09-07');
