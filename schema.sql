drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    author text not null,
    text text not null,
    data text
);

drop table if exists users;
create table users (
	id integer primary key autoincrement,
	username text not null,
	password text not null,
	name text,
	surname text,
	email text,
	color text,
	about text,
	ip text
);
