import pymysql as p
passwrd='vishesh14'
conn=p.connect(host='localhost',user='root',password=passwrd,database='bank')
cur=conn.cursor()

cmd=' create table if not exists Accounts (Serial int, AccNo decimal(14,0) primary key, Name varchar(60), Email varchar(70) not null, DAO date, Bal Decimal(14,0))'
cur.execute(cmd)
cmd=' create table if not exists Transactions (Serial int primary key, DOT date ,AccNo decimal(14,0), Amt decimal(14), Mode varchar(60), Int_Bal decimal(14), Final_Bal decimal(14))'
cur.execute(cmd)

sr,acc,nm,doa,dot,amt,mode,i_bal,f_bal,email=1,5490816372,'Admin','2023-05-22','2023-05-22',0,'CR',0,0,"virtualbankofindia@gmail.com"
cmd='insert into Accounts values ({},{},"{}","{}","{}",{})'.format(sr,acc,nm,email,doa,amt)
cur.execute(cmd)
conn.commit()
cmd='insert into Transactions values ({},"{}",{},{},"{}",{},{})'.format(sr,dot,acc,amt,mode,i_bal,f_bal)
cur.execute(cmd)
conn.commit()

conn.close()