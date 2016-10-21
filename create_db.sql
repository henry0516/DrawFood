-- create_db.sql
CREATE TABLE members (
	id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	name TEXT NOT NULL,
	group_name TEXT
);

CREATE TABLE draw_histories (
    draw_histories_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	memberid INTEGER,
	time DATETIME DEFAULT (datetime('now', 'localtime')),
	FOREIGN KEY (memberid) REFERENCES members(id)
);