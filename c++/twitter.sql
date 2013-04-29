\timing
create table follows (follower int, followee int);
copy follows from '/home/hyrkas/datalog_repo/datalogcompiler/c++/t_6200000' delimiter as ' ';
alter table follows add primary key (follower,followee);
create index follower_a on follows(follower);
create index follower_b on follows(followee);
--non distinct two-paths...238 seconds???
select count(*) from follows a, follows b where a.followee = b.follower;
--distinct two-paths
select count(*) from (select distinct a.follower, b.followee from follows a, follows b where a.followee = b.follower) c;

--check on how to allow postgres to use more main memory
