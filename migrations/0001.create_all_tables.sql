create table outcome_category
(
	id bigserial not null,
	name varchar(50),
    chat_id bigint,
    is_default bool not null default FALSE,
    is_deleted bool not null default FALSE
);

create unique index outcome_category_id_uindex
	on outcome_category (id);

alter table outcome_category
	add constraint outcome_category_pk
		primary key (id);

create table income
(
	id bigserial not null,
	username varchar(50),
	chat_id bigint not null,
	amount numeric(15,2),
	created_at timestamp(0) default now()
);

create unique index income_id_uindex
	on income (id);

alter table income
	add constraint income_pk
		primary key (id);


create table outcome
(
	id bigserial not null,
    chat_id bigint not null,
    category_id bigint
	    constraint outcome_category_id_fk
		references outcome_category (id),
	amount numeric(15,2),
	created_at timestamp(0) default now()
);

create unique index outcome_id_uindex
	on outcome (id);

alter table outcome
	add constraint outcome_pk
		primary key (id);


insert into outcome_category(name, is_default)
values ('🍞 Продукты', TRUE), ('🚖 Транспорт', TRUE);