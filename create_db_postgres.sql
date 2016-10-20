-- create_db.sql
CREATE TABLE members (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	group_name TEXT
);

CREATE TABLE draw_histories (
	memberid INTEGER REFERENCES members(id),
	time timestamp DEFAULT (current_timestamp)
);

--insert into members(name, group_name) values('Water','Cheap');
--insert into members(name, group_name) values('Bread','Cheap');
--INSERT INTO draw_histories (memberid) VALUES (1);
